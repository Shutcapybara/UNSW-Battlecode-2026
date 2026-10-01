#!/usr/bin/env python3
"""Resume source-frozen, paired Expedition games, serially, with replays.
Defaults to planning only. --execute starts at most --max-games inside the
admission budget. An already-started game is allowed to finish.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
from importlib.metadata import version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/rb'))
sys.path.insert(0, str(ROOT / 'tools/cx'))
import arena_lune
import panel
from tools.analysis.features.run_panel import runtime_fingerprint

STORE = ROOT / 'build/expedition/replay-panels'
QUEUE = ['expedition-09-mouthroute', 'expedition-08-symmetry', 'expedition-06-allycrowd',
         'expedition-02-threat05', 'expedition-03-revisit005', 'expedition-04-trap20',
         'expedition-05-explore3', 'expedition-07a-sparse48-160', 'expedition-07b-sparse48-384',
         'expedition-07c-sparse48-768', 'expedition-07d-sparse160-384', 'expedition-07e-sparse160-768']

# Explicitly selected focused experiments do not replace the original queue.
FOCUSED_CANDIDATE = 'expedition-10-mouthcontest'
SCREENS = {'mouth-contest-v1': dict(candidate=FOCUSED_CANDIDATE, seeds=[1, 2],
    maps=[('z1', 'queen_of_spades'), ('z1', 'portals'), ('z1', 'devil'),
          ('gen', 'new/mc26_portal_quartet')])}
CANDIDATES = QUEUE + [FOCUSED_CANDIDATE]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_id(bot):
    return runtime_fingerprint(str(ROOT / 'bots' / bot))


def run_dir(bot, pn):
    return STORE / f'{bot}-{source_id(bot)[:12]}' / pn


def contract(bot, pn):
    fixture_keys = sorted(panel.expected(pn, [1, 2, 3]))
    opps = sorted({k[3] for k in fixture_keys})
    maps = sorted({k[0] for k in fixture_keys})
    refs = ['field_references.json', 'field_distributions.json', 'map_reference_medians.json', 'tempo_reference.json']
    return dict(bot=bot, fingerprint=source_id(bot), panel=pn, seeds=[1, 2, 3],
                opponents={o: source_id(o) for o in opps}, maps={m: sha(ROOT / 'maps' / f'{m}.map') for m in maps},
                references={r: sha(ROOT / 'docs/analysis/benchmarks' / r) for r in refs},
                arena_sha256=sha(ROOT / 'tools/rb/arena_lune.py'), unswbc_version=version('unswbc'),
                host=socket.gethostname(), sandbox=False)


def freeze(bot, pn):
    dest = run_dir(bot, pn)
    dest.mkdir(parents=True, exist_ok=True)
    file = dest / 'contract.json'
    current = contract(bot, pn)
    if file.exists():
        if json.loads(file.read_text()) != current:
            raise ValueError(f'Frozen experiment inputs changed: {file}')
    else:
        file.write_text(json.dumps(current, indent=2) + '\n')
    return dest


def validate_row(row, bot, pn, dest, replay=None):
    key = (row['map'], row['side'], row['seed'], row['opp'])
    if (key not in panel.expected(pn, [1, 2, 3]) or row.get('errors')
            or Path(row['cand']).name != bot or row['result'] not in ('win', 'loss', 'draw')):
        raise ValueError(f'Invalid fixture: {key}')
    expected_replay = f'replays/{fixture_tag(bot, key)}.replay'
    if row['replay'] != expected_replay:
        raise ValueError(f'Misattributed replay: {key}')
    replay = replay or dest / row['replay']
    if not replay.exists() or sha(replay) != row['replay_sha256']:
        raise ValueError(f'Missing or changed replay: {replay}')
    if (row.get('candidate_fingerprint') != source_id(bot)
            or row.get('opponent_fingerprint') != source_id(row['opp'])):
        raise ValueError(f'Source mismatch: {key}')
    return key


def read_rows(bot, pn):
    dest = run_dir(bot, pn)
    out = {}
    path = dest / 'rows.jsonl'
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        row = json.loads(line)
        key = validate_row(row, bot, pn, dest)
        if key in out:
            raise ValueError(f'Duplicate fixture: {path}: {key}')
        out[key] = row
    return out


def append_row(dest, row):
    # Atomic whole-index replacement prevents a killed writer leaving a partial
    # JSON line. Only the process holding campaign.lock may call this.
    path = dest / 'rows.jsonl'
    tmp = dest / 'rows.jsonl.tmp'
    with tmp.open('w') as f:
        f.write(path.read_text() if path.exists() else '')
        f.write(json.dumps(row) + '\n')
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def recover(bot, pn):
    """Publish completed pending fixtures under the lock without replaying games."""
    dest = run_dir(bot, pn)
    for pending in sorted(dest.glob('*.pending.json')):
        row = json.loads(pending.read_text())
        rep = dest / row['replay']
        tmp = rep.with_suffix('.replay.tmp')
        key = validate_row(row, bot, pn, dest, rep if rep.exists() else tmp)
        rows = read_rows(bot, pn)
        if key in rows:
            if rows[key] != row:
                raise ValueError(f'Pending/index disagreement: {pending}')
        else:
            if not rep.exists():
                tmp.replace(rep)
            append_row(dest, row)
        pending.unlink()
        print('RECOVERED', bot, pn, key, flush=True)


def fixture_tag(bot, key):
    m, side, seed, opp = key
    a, b = (bot, opp) if side == 'A' else (opp, bot)
    return f's{seed}__{m.replace("/", "+")}__{a}__{b}'


def play(bot, pn, key):
    dest = freeze(bot, pn)
    m, side, seed, opp = key
    a, b = (bot, opp) if side == 'A' else (opp, bot)
    tag = fixture_tag(bot, key)
    rep = dest / 'replays' / f'{tag}.replay'
    tmp = rep.with_suffix('.replay.tmp')
    error_file = dest / 'failures' / f'{tag}.json'
    if error_file.exists():
        raise ValueError(f'Previous fixture failed; inspect before retrying: {error_file}')
    if tmp.exists() and not rep.exists():
        raise ValueError(f'Unfinished replay has no completed row; inspect before retrying: {tmp}')
    if rep.exists():
        # A crash between replay publication and row append is recoverable only
        # from a pending row; never blindly spend the same deterministic game again.
        raise ValueError(f'Unindexed completed replay; recover its pending row: {rep}')
    print('START', bot, pn, key, flush=True)
    result = arena_lune.run_game(str(ROOT / 'maps' / f'{m}.map'), str(ROOT / 'bots' / a),
                                 str(ROOT / 'bots' / b), seed, replay_out=str(tmp))
    us, them = ('A', 'B') if side == 'A' else ('B', 'A')
    row = dict(map=m, side=side, seed=seed, cand=f'bots/{bot}', opp=opp, sandbox=False,
               result='draw' if result['winner'] not in ('A', 'B') else 'win' if result['winner'] == us else 'loss',
               rounds=result['rounds'], us=result['stats'][us], them=result['stats'][them],
               errors=result['errors'], secs=result['secs'], end_reason=str(result['end_reason']),
               candidate_fingerprint=source_id(bot), opponent_fingerprint=source_id(opp),
               replay=str(rep.relative_to(dest)), replay_sha256=sha(tmp), host=socket.gethostname())
    if row['errors']:
        error_file.parent.mkdir(parents=True, exist_ok=True)
        error_file.write_text(json.dumps(row, indent=2) + '\n')
        raise RuntimeError(f'Bot/runtime errors on either team; evidence retained: {error_file}')
    pending = dest / f'{tag}.pending.json'
    journal_tmp = pending.with_suffix('.tmp')
    with journal_tmp.open('w') as f:
        f.write(json.dumps(row) + '\n')
        f.flush()
        os.fsync(f.fileno())
    journal_tmp.replace(pending)
    tmp.replace(rep)
    append_row(dest, row)
    pending.unlink()
    print('DONE', bot, row['result'], row['rounds'], 'rounds', row['secs'], 'seconds', flush=True)
    return row


def fixture_order(screen=None):
    if screen:
        spec = SCREENS[screen]
        for seed in spec['seeds']:
            for pn, map_name in spec['maps']:
                for key in sorted(panel.expected(pn, [seed])):
                    if key[0] == map_name:
                        yield pn, key
    else:
        for seed in (1, 2, 3):
            for pn in ('z1', 'gen'):
                for key in sorted(panel.expected(pn, [seed])):
                    yield pn, key


def freeze_screen(candidate, screen):
    if not screen:
        return
    if SCREENS[screen]['candidate'] != candidate:
        raise ValueError('Screen belongs to a different candidate')
    contract_path = ROOT / 'bots' / candidate / 'README.md'
    data = dict(spec=SCREENS[screen], candidate_fingerprint=source_id(candidate),
                declaration_sha256=sha(contract_path), fixtures=list(fixture_order(screen)))
    # Normalize tuple/list representation before comparing the durable contract.
    data = json.loads(json.dumps(data))
    dest = STORE / 'screens' / f'{screen}.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and json.loads(dest.read_text()) != data:
        raise ValueError(f'Frozen focused screen changed: {dest}')
    if not dest.exists():
        dest.write_text(json.dumps(data, indent=2) + '\n')


def jobs(candidate, screen=None):
    # Seed 1 gets both complete panels before seeds 2 and 3. Every new
    # candidate fixture is immediately paired with the shared parent fixture.
    rows = {pn: [(bot, read_rows(bot, pn)) for bot in (panel.PARENT, candidate)]
            for pn in ('z1', 'gen')}
    for pn, key in fixture_order(screen):
        for bot, done in rows[pn]:
            if key not in done:
                yield bot, pn, key


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', choices=CANDIDATES)
    ap.add_argument('--screen', choices=SCREENS)
    ap.add_argument('--execute', action='store_true')
    ap.add_argument('--minutes', type=float, default=20)
    ap.add_argument('--max-games', type=int, default=24)
    a = ap.parse_args()
    if a.screen:
        selected = SCREENS[a.screen]['candidate']
        if a.candidate and a.candidate != selected:
            ap.error('Screen belongs to a different candidate')
        a.candidate = selected
    if not 0 < a.minutes <= 60 or not 1 <= a.max_games <= 200:
        ap.error('Use a 0–60 minute admission budget and 1–200 games')
    os.environ['PYTHONPYCACHEPREFIX'] = '/tmp/expedition-pycache'
    os.chdir(ROOT)
    candidate = a.candidate or next((b for b in QUEUE if next(jobs(b), None) is not None), None)
    if candidate is None:
        print('All predeclared fixtures complete. Score and audit before adding experiments.')
        return
    first = next(jobs(candidate, a.screen), None)
    print(json.dumps(dict(candidate=candidate, next_fixture=first, execute=a.execute,
                          screen=a.screen, max_games=a.max_games, minutes=a.minutes, workers=1), indent=2), flush=True)
    if not a.execute or first is None:
        return
    STORE.mkdir(parents=True, exist_ok=True)
    with (STORE / 'campaign.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another Expedition campaign owns the lock; no games started.')
            return
        lock.seek(0)
        lock.truncate()
        lock.write(str(os.getpid()) + '\n')
        lock.flush()
        freeze_screen(candidate, a.screen)
        for bot in (panel.PARENT, candidate):
            for pn in ('z1','gen'):
                freeze(bot, pn)
                recover(bot, pn)
        started = time.monotonic(); estimate = 30.0; completed = 0
        for bot, pn, key in jobs(candidate, a.screen):
            if completed >= a.max_games or time.monotonic() - started + estimate > a.minutes * 60:
                break
            row = play(bot, pn, key)
            estimate = max(30.0, row['secs'] * 1.25)
            completed += 1
        progress = dict(candidate=candidate, screen=a.screen, completed_this_batch=completed, seconds=round(time.monotonic()-started,1),
                        next_fixture=next(jobs(candidate, a.screen),None), host=socket.gethostname())
        (STORE / 'progress.json').write_text(json.dumps(progress,indent=2)+'\n')
        print(json.dumps(progress,indent=2),flush=True)


if __name__ == '__main__':
    main()
