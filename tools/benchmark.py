#!/usr/bin/env python3
"""Common-panel benchmarking: collect, plan missing games, run and resume.

.venv/bin/python tools/benchmark.py plan --config benchmark.toml
.venv/bin/python tools/benchmark.py run experiment_data/benchmark_TIMESTAMP
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import CancelledError, FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from html import escape
import itertools
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import tomllib
import uuid

from filelock import FileLock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from compare_bot import FAULT, IGNORED, hashes, read_config, write_csv
from tools.benchmarking.tournament import MatchWorkers, atomic_write, play
from benchmark_data import aliases, collect, register_source, sha, with_rating_context
from game_stats import ROOT, digest, make_record, publish_games, read_parquet, write_parquet
from benchmark_weights import configured_distribution


def save(path, value):
    atomic_write(path, json.dumps(value, indent=2, allow_nan=False) + '\n')


def key(a, b, board):
    return json.dumps([a, b, board], separators=(',', ':'))


def load_config(path):
    config = tomllib.loads(path.read_text())
    extra = set(config) - {'bots', 'maps', 'references', 'pairing', 'run', 'map_distribution',
                           'context_manifest', 'map_name_policy', 'source_aliases'}
    if extra:
        raise ValueError(f'Unknown configuration keys: {sorted(extra)}')
    # Reuse the comparison runner's path and execution-setting validation.
    standard = {k: v for k, v in config.items() if k in ('bots', 'maps', 'run')}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', dir=path.parent) as handle:
        text = '\n'.join(f'{k} = {json.dumps(v)}' for k, v in standard.items() if k != 'run')
        text += '\n[run]\n' + '\n'.join(f'{k} = {json.dumps(v)}' for k, v in standard.get('run', {}).items())
        handle.write(text); handle.flush()
        bots, maps, settings = read_config(Path(handle.name), path.parent / '__no_candidate__')
    map_name_policy = config.get('map_name_policy', 'stem')
    if map_name_policy not in ('stem', 'maps_relative'):
        raise ValueError('map_name_policy must be "stem" or "maps_relative"')
    if map_name_policy == 'maps_relative':
        map_root = (ROOT / 'maps').resolve()
        named_maps = {}
        for source in maps.values():
            try:
                name = source.resolve().relative_to(map_root).with_suffix('').as_posix()
            except ValueError:
                raise ValueError('maps_relative requires every map to be under maps/') from None
            if name in named_maps:
                raise ValueError(f'Duplicate map path: {name}')
            named_maps[name] = source
        maps = named_maps
    source_aliases = config.get('source_aliases', {})
    if (not isinstance(source_aliases, dict) or
            any(not isinstance(source, str) or len(source) != 64 or
                any(ch not in '0123456789abcdef' for ch in source) or
                not isinstance(effective, str) or len(effective) != 64 or
                any(ch not in '0123456789abcdef' for ch in effective)
                for source, effective in source_aliases.items())):
        raise ValueError('source_aliases must map lowercase SHA-256 fingerprints to fingerprints')
    if set(settings['sides']) != {'A', 'B'}:
        raise ValueError('Benchmarks require both sides')
    references = config.get('references', [])
    pairing = config.get('pairing', 'panel')
    if pairing not in ('panel', 'round_robin', 'adaptive') or (pairing == 'panel' and not references):
        raise ValueError('Choose panel with references, or round_robin')
    if len(set(references)) != len(references) or set(references) - bots.keys():
        raise ValueError('References must be unique names in the bot roster')
    configured_distribution(config, maps, path)
    return bots, maps, settings, references, pairing


def targets(manifest):
    names, refs = manifest['bots'], set(manifest['references'])
    return {(a, b, board) for a, b in itertools.permutations(names, 2)
            if manifest['pairing'] != 'panel' or a in refs or b in refs
            for board in manifest['maps']}


def observed(manifest, rows, source_aliases):
    """Only matching sources, maps and runtime can fill a current fixture."""
    result = defaultdict(list)
    for row in rows:
        a, b, board = row['bot_a'], row['bot_b'], row['map']
        if (a not in manifest['bots'] or b not in manifest['bots'] or board not in manifest['maps']
                or row['mode'] != manifest['mode'] or row['runner_version'] != manifest['runner_version']
                or row['seed'] is not None or row['map_sha256'] != manifest['map_hashes'][board]):
            continue
        if any(source_aliases.get(row['bot_' + side + '_sha256'], row['bot_' + side + '_sha256']) !=
               manifest['effective_hashes'][name] for side, name in (('a', a), ('b', b))):
            continue
        result[a, b, board].append(row)
    return result


def ordered_gaps(manifest, seen):
    """Equalize reference coverage; interleave opponents/maps in paired-side blocks."""
    wanted = targets(manifest)
    refs = set(manifest['references'])
    own = {n: {f for f in wanted if n in f[:2] and
               (manifest['pairing'] == 'round_robin' or (f[1] if f[0] == n else f[0]) in refs)}
           for n in manifest['bots']}
    virtual = set(seen) & wanted
    remaining = wanted - virtual
    queue = []
    while remaining:
        eligible = [n for n, fixtures in own.items() if fixtures & remaining]
        owner = min(eligible, key=lambda n: (len(own[n] & virtual) / len(own[n]), digest(n)))
        available = own[owner] & remaining
        counts = Counter((b if a == owner else a) for a, b, m in own[owner] & virtual)
        boards = Counter(m for a, b, m in own[owner] & virtual)
        def priority(f):
            a, b, board = f
            opponent = b if a == owner else a
            return ((b, a, board) not in virtual, counts[opponent], boards[board], digest([owner, opponent, board]), a)
        a, b, board = min(available, key=priority)
        block = [f for f in [(a, b, board), (b, a, board)] if f in remaining]
        queue.extend(block); virtual.update(block); remaining.difference_update(block)
    return queue


def report(out, manifest, rows, source_aliases):
    with FileLock(str(out/'.report.lock'),timeout=120):
        return write_report(out,manifest,rows,source_aliases)


def adaptive_progress(manifest, rows, source_aliases):
    games=observed(manifest,rows,source_aliases)
    n,m=len(manifest['bots']),len(manifest['maps'])
    return dict(updated=datetime.now(timezone.utc).isoformat(),bots=n,maps=m,
        ledger_games=len(rows),matching_games=sum(map(len,games.values())),
        target_fixtures=n*(n-1)*m,completed_fixtures=len(games),
        missing_fixtures=n*(n-1)*m-len(games))


def write_report(out, manifest, rows, source_aliases):
    games = observed(manifest, rows, source_aliases)
    wanted = targets(manifest)
    refs = set(manifest['references'])
    scores = {f: sum(1 if r['outcome'] == 'A' else .5 if r['outcome'] == 'draw' else 0
                     for r in records) / len(records) for f, records in games.items()}
    summaries, pairs = [], []
    for bot in manifest['bots']:
        opponents = [n for n in manifest['bots'] if n != bot and
                     (manifest['pairing'] != 'panel' or n in refs)]
        desired = {f for f in wanted if bot in f[:2] and (f[1] if f[0] == bot else f[0]) in opponents}
        completed = desired & games.keys()
        paired, paired_scores = 0, []
        for opponent in manifest['bots']:
            if opponent == bot:
                continue
            observed_scores, paired_values = [], []
            for board in manifest['maps']:
                ab, ba = (bot, opponent, board), (opponent, bot, board)
                observed_scores += ([scores[ab]] if ab in games else [])
                observed_scores += ([1 - scores[ba]] if ba in games else [])
                if ab in games and ba in games:
                    paired_values.append((scores[ab] + 1 - scores[ba]) / 2)
            if opponent in opponents:
                paired += len(paired_values); paired_scores += paired_values
            pairs.append(dict(bot=bot, opponent=opponent, fixtures=len(observed_scores),
                paired_maps=len(paired_values), score=sum(observed_scores)/len(observed_scores) if observed_scores else None))
        raw = [r for f, values in games.items() if bot in f[:2] for r in values]
        wins = sum(r['outcome'] == ('A' if r['bot_a'] == bot else 'B') for r in raw)
        draws = sum(r['outcome'] == 'draw' for r in raw)
        summaries.append(dict(bot=bot, games=len(raw), wins=wins, draws=draws, losses=len(raw)-wins-draws,
            target_fixtures=len(desired), completed_fixtures=len(completed), missing=len(desired-completed),
            paired_maps=paired, target_paired_maps=len(desired)//2,
            paired_score=sum(paired_scores)/len(paired_scores) if paired_scores else None))
    summaries.sort(key=lambda r: (r['completed_fixtures']/max(1, r['target_fixtures']), r['bot']))
    write_csv(out / 'coverage.csv', summaries)
    write_csv(out / 'pairwise.csv', pairs)
    write_csv(out / 'per_map.csv', [dict(bot_a=a, bot_b=b, map=m, games=len(rs),
        a_wins=sum(r['outcome']=='A' for r in rs), b_wins=sum(r['outcome']=='B' for r in rs),
        draws=sum(r['outcome']=='draw' for r in rs), a_score=scores[a,b,m]) for (a,b,m),rs in sorted(games.items())])
    summary = dict(updated=datetime.now(timezone.utc).isoformat(), bots=len(manifest['bots']),
        maps=len(manifest['maps']), ledger_games=len(rows), matching_games=sum(map(len,games.values())),
        target_fixtures=len(wanted), completed_fixtures=len(wanted & games.keys()),
        missing_fixtures=len(wanted - games.keys()),
        bots_without_reference_games=sum(r['completed_fixtures']==0 for r in summaries),
        conflicting_fixtures=sum(len({r['outcome'] for r in rs}) > 1 for rs in games.values()))
    save(out / 'coverage.json', summary)
    page = ['<!doctype html><meta charset="utf-8"><title>Bot benchmark coverage</title>',
        '<style>body{font:15px system-ui;margin:30px;color:#243340}table{border-collapse:collapse}td,th{padding:7px;border-bottom:1px solid #ddd;text-align:right}td:first-child,th:first-child{text-align:left}.matrix{overflow:auto;max-height:650px}.matrix td{font-size:10px;min-width:24px;padding:3px}th{position:sticky;top:0;background:white}</style>',
        '<h1>Bot benchmark coverage</h1>', f'<p>{summary["completed_fixtures"]:,} / {len(wanted):,} target fixtures observed; '
        f'{summary["missing_fixtures"]:,} missing. {len(manifest["bots"])} frozen bot versions, {len(manifest["maps"])} maps.</p>',
        '<p>Ordered by coverage, not strength. Paired score uses only completed side-swapped map pairs against the reference panel. '
        'Scores with different missing cells are not directly comparable. Repeated fixtures count once for coverage; their scores are averaged. '
        'Missing games are blank, never draws. Native execution does not establish judge CPU compliance.</p>',
        '<p><a href="coverage.csv">Coverage</a> · <a href="pairwise.csv">Pairwise results</a> · '
        '<a href="per_map.csv">Per-map results</a> · <a href="import_audit.json">Import inventory</a> · <a href="manifest.json">Frozen manifest</a></p>',
        '<table><tr><th>Bot</th><th>Reference fixtures</th><th>Paired map cells</th><th>Paired score</th><th>All matching W / D / L</th></tr>']
    for r in summaries:
        score = '—' if r['paired_score'] is None else f'{100*r["paired_score"]:.1f}%'
        page.append(f'<tr><td>{escape(r["bot"])}</td><td>{r["completed_fixtures"]}/{r["target_fixtures"]}</td>'
            f'<td>{r["paired_maps"]}/{r["target_paired_maps"]}</td><td>{score}</td><td>{r["wins"]} / {r["draws"]} / {r["losses"]}</td></tr>')
    page += ['</table><h2>Matchup coverage</h2><p>Cell = observed directional fixtures out of '
             f'{2*len(manifest["maps"])}. Hover for opponent and score.</p><div class="matrix"><table>']
    pair_index = {(r['bot'],r['opponent']):r for r in pairs}
    for i, bot in enumerate(manifest['bots']):
        page.append(f'<tr><td>{i+1}. {escape(bot)}</td>')
        for j, opp in enumerate(manifest['bots']):
            r = pair_index.get((bot,opp)); count = r['fixtures'] if r else 0
            title = f'{j+1}. {opp}: {count} fixtures' + (f', score {r["score"]:.3f}' if count else '')
            page.append(f'<td title="{escape(title)}" style="background:rgba(36,150,120,{count/(2*len(manifest["maps"])):.2f})">{count or ""}</td>')
        page.append('</tr>')
    atomic_write(out/'index.html', '\n'.join(page)+'</table></div>')
    return summary


def prepare(config):
    bots, maps, settings, references, pairing = load_config(config)
    spec = tomllib.loads(config.read_text())
    weights, weight_policy = configured_distribution(spec, maps, config)
    context_path = (config.parent/spec['context_manifest']).resolve() if 'context_manifest' in spec else None
    context = json.loads(context_path.read_text()) if context_path else None
    if context is not None and context.get('benchmark_version') != 1:
        raise ValueError('Rating context must be an existing benchmark manifest')
    executable = shutil.which('unswbc')
    if not executable:
        raise ValueError('unswbc is not on PATH')
    audit = collect()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
    out = ROOT/'experiment_data'/('benchmark_'+stamp)
    out.mkdir(parents=True)
    manifest = dict(benchmark_version=1, run_id=uuid.uuid4().hex, created=datetime.now(timezone.utc).isoformat(),
        bots=sorted(bots), maps=sorted(maps), references=references, pairing=pairing, settings=settings,
        mode='sandbox' if settings['sandbox'] else 'native', runner=executable,
        runner_version=subprocess.check_output([executable,'--version'],text=True).strip(),
        hashes={}, effective_hashes={}, map_hashes={}, map_weights=weights,
        map_weight_policy=weight_policy, source_aliases=spec.get('source_aliases', {}))
    if context is not None:
        manifest['rating_context'] = dict(manifest=str(context_path), sha256=sha(context_path),
            effective_hashes={n: h for n, h in with_rating_context(context)['effective_hashes'].items()
                              if n not in bots})
        save(out/'rating-context-manifest.json', context)
    for name, source in bots.items():
        target=out/'sources/bots'/name
        before=hashes(source)
        shutil.copytree(source,target,ignore=shutil.ignore_patterns(*IGNORED))
        if hashes(target)!=before or hashes(source)!=before:
            raise ValueError(f'Bot changed during snapshot: {name}; create a new plan')
        manifest['hashes']['bots/'+name]=before
        manifest['effective_hashes'][name]=register_source(before,target)
    (out/'sources/maps').mkdir(parents=True)
    for name, source in maps.items():
        target=out/'sources/maps'/(name+'.map'); target.parent.mkdir(parents=True, exist_ok=True); before=sha(source)
        shutil.copy2(source,target)
        if sha(target)!=before or sha(source)!=before:
            raise ValueError(f'Map changed during snapshot: {name}')
        manifest['map_hashes'][name]=before
    # Detect any map/weight manifest changes during snapshot creation.
    if configured_distribution(tomllib.loads(config.read_text()), maps, config) != (weights, weight_policy):
        raise ValueError('Map distribution changed during snapshot')
    if weight_policy['kind'] == 'suite_mixture':
        shutil.copy2(weight_policy['manifest'], out/'map-suite-manifest.json')
    shutil.copy2(config,out/'benchmark.toml')
    save(out/'manifest.json',manifest); save(out/'import_audit.json',audit)
    source_aliases=aliases()
    for source, effective in manifest['source_aliases'].items():
        if effective not in manifest['effective_hashes'].values():
            raise ValueError(f'Source alias target is not in this bot roster: {source}')
        if source in source_aliases and source_aliases[source] != effective:
            raise ValueError(f'Conflicting source alias: {source}')
        source_aliases[source] = effective
    save(out/'aliases.json',source_aliases)
    rows=read_parquet(ROOT/'game_stats.parquet'); write_parquet(out/'initial_games.parquet',rows)
    queue=[] if pairing=='adaptive' else ordered_gaps(manifest,observed(manifest,rows,source_aliases))
    save(out/'plan.json',queue)
    summary=(adaptive_progress(manifest,rows,source_aliases) if pairing=='adaptive'
             else report(out,manifest,rows,source_aliases))
    print(json.dumps(dict(directory=str(out),**summary),indent=2),flush=True)
    return out


def record(manifest, game):
    a,b,board=game['team_a'],game['team_b'],game['map']
    return make_record(run_id=manifest['run_id'],game_key=key(a,b,board),source='benchmark',
        run_started_at=manifest['created'],bot_a=a,bot_b=b,
        bot_a_sha256=digest(manifest['hashes']['bots/'+a]),bot_b_sha256=digest(manifest['hashes']['bots/'+b]),
        map_name=board,map_sha256=manifest['map_hashes'][board],mode=manifest['mode'],
        runner_version=manifest['runner_version'],outcome=game['outcome'],rounds=game['rounds'],
        runtime_faults=game.get('runtime_faults'))


def run(out, limit=None, jobs=None, replays=True, retry_errors=False):
    manifest=json.loads((out/'manifest.json').read_text())
    if manifest.get('benchmark_version')!=1:
        raise ValueError('Unsupported benchmark manifest')
    if subprocess.check_output([manifest['runner'],'--version'],text=True).strip()!=manifest['runner_version']:
        raise ValueError('Toolkit version changed; prepare a new benchmark')
    for name in manifest['bots']:
        if hashes(out/'sources/bots'/name)!=manifest['hashes']['bots/'+name]:
            raise ValueError(f'Frozen source changed: {name}')
    for board in manifest['maps']:
        if sha(out/'sources/maps'/(board+'.map'))!=manifest['map_hashes'][board]:
            raise ValueError(f'Frozen map changed: {board}')
    source_aliases=aliases() | json.loads((out/'aliases.json').read_text())
    blocked_path=out/'blocked-bots.json'
    blocked=set(json.loads(blocked_path.read_text())) if blocked_path.exists() and not retry_errors else set()
    if blocked-set(manifest['bots']):
        raise ValueError('Blocked bots must belong to the frozen roster')
    count=0; pending=[]; status='running'; stopped=False
    def stop(signum, frame):
        nonlocal stopped
        stopped=True
    previous={s:signal.signal(s,stop) for s in (signal.SIGINT,signal.SIGTERM)}
    previous_cache=os.environ.get('PYTHONPYCACHEPREFIX')
    (out/'games').mkdir(exist_ok=True)
    with FileLock(str(out/'.run.lock'),timeout=0), sqlite3.connect(out/'results.sqlite3') as db:
        db.execute('CREATE TABLE IF NOT EXISTS games (fixture TEXT PRIMARY KEY, data TEXT NOT NULL)')
        saved=[json.loads(r[0]) for r in db.execute('SELECT data FROM games')]
        publish_games([record(manifest,g) for g in saved if g['outcome']!='error'],ROOT)
        errors={key(g['team_a'],g['team_b'],g['map']) for g in saved if g['outcome']=='error'}
        rows=read_parquet(ROOT/'game_stats.parquet')
        seen=set(observed(manifest,rows,source_aliases))
        queue=iter(tuple(f) for f in json.loads((out/'plan.json').read_text())
                   if tuple(f) not in seen and (retry_errors or key(*f) not in errors))
        def flush():
            nonlocal rows,seen,pending
            if pending:
                publish_games(pending,ROOT); pending=[]
            rows=read_parquet(ROOT/'game_stats.parquet')
            seen=set(observed(manifest,rows,source_aliases))
            coverage=(adaptive_progress(manifest,rows,source_aliases) if manifest['pairing']=='adaptive'
                      else report(out,manifest,rows,source_aliases))
            save(out/'progress.json',dict(status=status,new_games=count,blocked_bots=sorted(blocked),
                saved_errors=len(errors),**coverage))
            save(blocked_path,sorted(blocked))
        flush()  # Publish startup/resume health before the first potentially long game.
        settings=manifest['settings']; concurrency=jobs or settings['jobs']
        last_flush=time.monotonic()
        try:
            with tempfile.TemporaryDirectory(prefix='benchmark-workers-') as workspace:
                # Apple's Python otherwise tries to compile into ~/Library/Caches,
                # outside the writable workspace of local coding agents.
                os.environ['PYTHONPYCACHEPREFIX']=str(Path(workspace)/'pycache')
                workers=MatchWorkers(workspace)
                with ThreadPoolExecutor(max_workers=concurrency) as pool:
                    futures={}; submitted=0; exhausted=False
                    try:
                        while futures or not exhausted:
                            while not stopped and not exhausted and len(futures)<concurrency:
                                if limit is not None and submitted>=limit:
                                    exhausted=True; break
                                f=next(queue,None)
                                if f is None:
                                    if manifest['pairing']=='adaptive':
                                        # Finish the batch before fitting to its new evidence.
                                        if futures:
                                            break
                                        from benchmark_priority import adaptive_batch
                                        flush()
                                        missing,detail=adaptive_batch(manifest,
                                            observed(with_rating_context(manifest),rows,source_aliases),
                                            excluded=[] if retry_errors else [tuple(json.loads(k)) for k in errors],blocked=blocked)
                                        detail['updated']=datetime.now(timezone.utc).isoformat()
                                        save(out/'adaptive-plan.json',detail)
                                        print(f'Adaptive batch: {len(missing)} games; {detail["reason_counts"]}',flush=True)
                                        queue=iter(missing)
                                        f=next(queue,None)
                                    if f is None:
                                        exhausted=True; break
                                a,b,board=f
                                if f in seen or a in blocked or b in blocked:
                                    continue
                                label=digest(f)[:20]
                                future=pool.submit(play,manifest['runner'],out/'sources/maps'/(board+'.map'),
                                    out/'sources/bots'/a,out/'sources/bots'/b,out/'games',label,
                                    settings['timeout_seconds'],replays,workers,settings['sandbox'],
                                    board_id=board)
                                futures[future]=f; submitted+=1
                            if stopped:
                                workers.cancel(); exhausted=True
                            if not futures:
                                break
                            done,_=wait(futures,timeout=1,return_when=FIRST_COMPLETED)
                            for future in done:
                                f=futures.pop(future)
                                if future.cancelled():
                                    continue
                                try:
                                    game=future.result()
                                except CancelledError:
                                    if stopped:
                                        continue
                                    raise
                                # Interrupted games remain pending and are retryable on resume.
                                if stopped and game['outcome']=='error':
                                    continue
                                log=(out/'games'/game['log']).read_text(errors='replace')
                                game['runtime_faults']=len(FAULT.findall(log)) if settings['sandbox'] else None
                                db.execute('INSERT OR REPLACE INTO games VALUES (?,?)',(key(*f),json.dumps(game)))
                                db.commit(); count+=1
                                if game['outcome']=='error':
                                    errors.add(key(*f)); blocked.update(f[:2])
                                else:
                                    errors.discard(key(*f)); pending.append(record(manifest,game)); seen.add(f)
                                print(f'{count}: {f[0]} vs {f[1]} / {f[2]}: {game["outcome"]}',flush=True)
                            if len(pending)>=32 or time.monotonic()-last_flush>=60:
                                flush(); last_flush=time.monotonic()
                    finally:
                        workers.cancel()
            status='stopped' if stopped else 'batch_complete'
        except BaseException:
            status='failed'
            raise
        finally:
            flush()
            for s,handler in previous.items(): signal.signal(s,handler)
            if previous_cache is None:
                os.environ.pop('PYTHONPYCACHEPREFIX',None)
            else:
                os.environ['PYTHONPYCACHEPREFIX']=previous_cache


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    plan=commands.add_parser('plan'); plan.add_argument('--config',type=Path,default=ROOT/'benchmark.toml')
    execute=commands.add_parser('run'); execute.add_argument('directory',type=Path)
    execute.add_argument('--max-games',type=int); execute.add_argument('--jobs',type=int)
    execute.add_argument('--no-replays',action='store_true'); execute.add_argument('--retry-errors',action='store_true')
    view=commands.add_parser('report'); view.add_argument('directory',type=Path)
    args=parser.parse_args()
    if args.command=='plan':
        prepare(args.config.resolve())
    elif args.command=='run':
        if (args.jobs is not None and args.jobs<1) or (args.max_games is not None and args.max_games<1):
            parser.error('jobs and max-games must be positive')
        run(args.directory.resolve(),args.max_games,args.jobs,not args.no_replays,args.retry_errors)
    else:
        out=args.directory.resolve(); manifest=json.loads((out/'manifest.json').read_text())
        print(json.dumps(report(out,manifest,read_parquet(ROOT/'game_stats.parquet'),
            aliases() | json.loads((out/'aliases.json').read_text())),indent=2))


if __name__=='__main__':
    main()
