"""Live monitor for Phase 3 (Live ops, lane Daichi): writes docs/learning/live.md.

Reads only repository-side data (no API calls, no hub database):
  public_replays/corpus/index.jsonl  — every collected game; team 7's own games carry `bot_a`/`bot_b`
                                       (replay-header submission ids), so ranked games attribute to a submission;
  public_replays/corpus/ladder/*.json — ladder snapshots (~10 min), for Elo expectations and the top-ten roster;
  hub-state/status.json, hub-state/candidates.json — the live submission and its fingerprint.

Statistic: per ranked game, score (1 / 0.5 / 0) minus the Elo expectation 1/(1+10^((R_opp−R_us)/400)), both ratings from
the last snapshot at or before the game's start. Intervals: whole-series cluster bootstrap (series_id), 1,000
resamples, seed 7, 5th/95th percentiles. Rollback trigger (Chair's rule, macro §4 / D-045 draft): rolling 40 ranked
games with mean < −0.08 AND 95th percentile < 0. Ranked and unranked are separate populations; unranked is listed
for exposure only.

Usage (repo root): python3 tools/daichi/live_monitor.py [--out docs/learning/live.md] [--json build/daichi/live.json]
"""
import argparse
import bisect
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

TEAM = 7
# D-052 §E: Schooltime and Prisoners Dilemma are played in two layouts each. Variant by the replay's map_hash
# (Shenzhen unit 7, docs/findings/2026-10-04-shenzhen-unit7-live-map-identity.md: one replay per hash, embedded map
# text vs maps/live/). Hashes not listed (pre-04:31Z 2 Oct, or new ones) report as 'other'.
VARIANTS = {
    'Schooltime': {'23fa2e8a800a': 'open4', '85635a271dcb': 'open4', '65be5fe99a46': 'template', 'e35816d70a75': 'template'},
    'Prisoners Dilemma': {'a9a230ecffab': '10 dragons', 'aebe7fff18a8': '10 dragons', '88eea47e61ff': 'template', 'dd78b14952c0': 'template'},
}
REPO = Path(__file__).resolve().parents[2]


# Style roster (rosters rule §9), from Kageyama's docs/learning/top-teams.md v1 (2026-10-04 13:55Z)
STYLE = (306, 264, 213, 952)

def ts(s):
    return datetime.fromisoformat(str(s).replace('Z', '+00:00'))


def load_ladders(dirpath, since):
    out = []
    for p in sorted(Path(dirpath).glob('*.json')):
        try:
            at = datetime.strptime(p.stem, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if at < since:
            continue
        try:
            rows = json.loads(p.read_text())
        except ValueError:
            continue
        rows = rows.get('ladder', rows) if isinstance(rows, dict) else rows
        out.append((at, {r['id']: r for r in rows if isinstance(r, dict) and 'id' in r}))
    return out


def rating_at(ladders, keys, when, team, with_key=False):
    """Elo of `team` from the last snapshot at or before `when`; None when no such snapshot exists.

    D-051 §4 fix: a game that precedes the earliest snapshot gets no expectation (it used to take snapshot 0,
    which is later than the game)."""
    i = bisect.bisect_right(keys, when) - 1
    for j in range(i, -1, -1):
        r = ladders[j][1].get(team)
        if r and r.get('elo') is not None:
            return (r['elo'], keys[j]) if with_key else r['elo']
    return (None, None) if with_key else None


def own_games(index_path, since):
    out = []
    with open(index_path) as fh:
        for line in fh:
            if '"team_a": 7,' not in line and '"team_b": 7,' not in line:
                continue
            r = json.loads(line)
            if TEAM not in (r.get('team_a'), r.get('team_b')) or r.get('status') != 'completed':
                continue
            start = r.get('started_at') or r.get('requested_at')
            if not start or ts(start) < since:
                continue
            side = 'a' if r['team_a'] == TEAM else 'b'
            w = (r.get('winner') or '').lower()
            score = 0.5 if w in ('draw', '') else float(w == side)
            out.append(dict(game_id=r['game_id'], series=r.get('series_id') or str(r['game_id']), at=ts(start), ranked=bool(r.get('ranked')),
                            bot=str(r.get('bot_' + side) or ''), opp=r['team_b'] if side == 'a' else r['team_a'], map=r.get('map_name'), map_hash=(r.get('map_hash') or '')[:12],
                            score=score, autoscrim=r.get('autoscrim_window'), requested_by=r.get('requested_by')))
    out.sort(key=lambda g: (g['at'], g['game_id']))
    return out


def boot(games, key='resid', resamples=1000, seed=7):
    if not games:
        return None
    by = {}
    for g in games:
        by.setdefault(g['series'], []).append(g[key])
    ser = sorted(by)
    rng = random.Random(seed)
    vals = []
    for _ in range(resamples):
        pick = [by[rng.choice(ser)] for _ in ser]
        n = sum(len(p) for p in pick)
        vals.append(sum(sum(p) for p in pick) / n)
    vals.sort()
    mean = sum(g[key] for g in games) / len(games)
    return dict(n=len(games), series=len(ser), mean=round(mean, 3), lo5=round(vals[int(.05 * resamples)], 3), hi95=round(vals[int(.95 * resamples) - 1], 3))


def fmt(b):
    if not b:
        return 'n 0'
    return f"{b['mean']:+.3f} [{b['lo5']:+.3f}, {b['hi95']:+.3f}] (n {b['n']} games / {b['series']} series)"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default=str(REPO))
    ap.add_argument('--out', default='docs/learning/live.md')
    ap.add_argument('--json', default='build/daichi/live.json')
    ap.add_argument('--days', type=int, default=14)
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=a.days)
    status = json.loads((repo / 'hub-state/status.json').read_text())
    active = status.get('active')
    cands = json.loads((repo / 'hub-state/candidates.json').read_text()) if (repo / 'hub-state/candidates.json').exists() else []
    cands = cands.get('candidates', cands) if isinstance(cands, dict) else cands
    inc = next((c for c in cands if isinstance(c, dict) and active in (c.get('submission'), c.get('submission_id'))), {})
    ladders = load_ladders(repo / 'public_replays/corpus/ladder', since - timedelta(hours=2))
    keys = [t for t, _ in ladders]
    games = own_games(repo / 'public_replays/corpus/index.jsonl', since)
    for g in games:
        (ru, ku), (ro, ko) = rating_at(ladders, keys, g['at'], TEAM, True), rating_at(ladders, keys, g['at'], g['opp'], True)
        g['snap_us'], g['snap_opp'] = ku and ku.strftime('%Y%m%dT%H%M%SZ'), ko and ko.strftime('%Y%m%dT%H%M%SZ')
        g['exp'] = None if ru is None or ro is None else 1 / (1 + 10 ** ((ro - ru) / 400))
        g['resid'] = None if g['exp'] is None else g['score'] - g['exp']
    ranked = [g for g in games if g['ranked'] and g['resid'] is not None]
    inc_ranked = [g for g in ranked if g['bot'] == str(active)]
    first_seen = min((g['at'] for g in games if g['bot'] == str(active)), default=None)
    roll = boot(inc_ranked[-40:])
    first40 = boot(inc_ranked[:40])
    # The rollback rule binds a *promoted* candidate after its first 40 ranked games; the rolling window is a drift signal.
    trigger = bool(first40 and first40['n'] >= 40 and first40['mean'] < -0.08 and first40['hi95'] < 0)
    drift_flag = bool(roll and roll['n'] >= 40 and roll['mean'] < -0.08 and roll['hi95'] < 0)
    latest = ladders[-1][1] if ladders else {}
    top10 = [t for t, r in sorted(latest.items(), key=lambda kv: kv[1].get('rank') or 10**9) if t != TEAM and not r.get('dev')][:10]
    band_cut = now - timedelta(hours=48)
    band = sorted({g['opp'] for g in ranked if g['at'] >= band_cut})
    per_opp = {}
    for g in inc_ranked:
        per_opp.setdefault(g['opp'], []).append(g['resid'])
    regression = sorted(o for o, v in per_opp.items() if len(v) >= 5 and sum(v) / len(v) > 0)
    rosters = dict(band=band, top=top10, style=list(STYLE), regression=regression)
    roster_stats = {k: boot([g for g in inc_ranked if g['opp'] in set(v)]) for k, v in rosters.items()}

    def elo_ago(hours):
        when = now - timedelta(hours=hours)
        return rating_at(ladders, keys, when, TEAM) if ladders and keys[0] <= when else None
    elo_now = (latest.get(TEAM) or {}).get('elo')
    rank_now = (latest.get(TEAM) or {}).get('rank')
    wk = now - timedelta(days=7)
    this_week = boot([g for g in ranked if g['at'] >= wk])
    prev_week = boot([g for g in ranked if wk - timedelta(days=7) <= g['at'] < wk])
    by_bot = {}
    for g in ranked:
        by_bot.setdefault(g['bot'] or '?', []).append(g)
    by_map = {}
    for g in inc_ranked:
        by_map.setdefault(g['map'], []).append(g)
        if g['map'] in VARIANTS:
            by_map.setdefault(f"{g['map']} · {VARIANTS[g['map']].get(g['map_hash'], 'other')}", []).append(g)
    unranked_inc = [g for g in games if not g['ranked'] and g['bot'] == str(active)]
    data = dict(at=now.isoformat(), active=active, incumbent=inc.get('name'), fingerprint=inc.get('fingerprint'), first_seen=str(first_seen),
                ranked_since=len(inc_ranked), wld=[sum(g['score'] == 1 for g in inc_ranked), sum(g['score'] == 0 for g in inc_ranked), sum(g['score'] == .5 for g in inc_ranked)],
                since_activation=boot(inc_ranked), first40=first40, rolling40=roll, rollback_trigger=trigger, drift_flag=drift_flag, rosters=rosters, roster_stats=roster_stats,
                elo=dict(now=elo_now, rank=rank_now, h24=elo_ago(24), d7=elo_ago(24 * 7)), drift=dict(this_week=this_week, prev_week=prev_week),
                by_bot={b: boot(v) for b, v in by_bot.items()}, by_map={m: boot(v) for m, v in by_map.items()}, unranked_since=len(unranked_inc),
                ladder_snapshots=len(ladders), latest_snapshot=str(keys[-1]) if keys else None,
                missing_expectation=sum(1 for g in games if g['ranked'] and g['resid'] is None))
    # D-051 §4: freeze the input list (game ids, snapshot ids) behind every published number.
    import hashlib
    frozen = dict(at=now.isoformat(), index_sha256=hashlib.sha256((repo / 'public_replays/corpus/index.jsonl').read_bytes()).hexdigest(),
                  snapshots=[k.strftime('%Y%m%dT%H%M%SZ') for k in keys],
                  games=[[g['game_id'], g['series'], g['at'].isoformat(), g['bot'], g['opp'], g['map'], g['ranked'], g['score'],
                          g['snap_us'], g['snap_opp'], None if g['exp'] is None else round(g['exp'], 6), g['map_hash']] for g in games],
                  columns=['game_id', 'series', 'start', 'bot', 'opp', 'map', 'ranked', 'score', 'snap_us', 'snap_opp', 'exp', 'map_hash12'])
    fz = json.dumps(frozen, separators=(',', ':'), default=str).encode()
    fsha = hashlib.sha256(fz).hexdigest()
    fdir = repo / Path(a.out).parent / 'live-inputs'
    fdir.mkdir(parents=True, exist_ok=True)
    fname = f"{now.strftime('%Y%m%dT%H%MZ')}-{fsha[:8]}.json.gz"  # sha256 is of the uncompressed JSON
    import gzip
    (fdir / fname).write_bytes(gzip.compress(fz, mtime=0))
    data['frozen_inputs'] = dict(file='docs/learning/live-inputs/' + fname, sha256=fsha, games=len(games), snapshots=len(keys))
    Path(repo / a.json).parent.mkdir(parents=True, exist_ok=True)
    (repo / a.json).write_text(json.dumps(data, indent=1, default=str))
    L = []
    L.append('# Live monitor (Live ops, lane Daichi)\n')
    L.append(f"Generated {now.strftime('%Y-%m-%d %H:%M UTC')} by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, "
             f"replay-header attribution) and {len(ladders)} ladder snapshots (latest {data['latest_snapshot']}). Population: **ranked** "
             f"games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 "
             f"resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).\n")
    L.append(f"Frozen inputs (D-051 §4): `docs/learning/live-inputs/{fname}` sha256 `{fsha[:16]}…` "
             f"({len(games)} games with their snapshot ids, {len(keys)} snapshots, index sha `{frozen['index_sha256'][:12]}`). "
             f"Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.\n")
    L.append('## Incumbent\n')
    L.append(f"- Live submission **{active}** ({inc.get('name') or 'not a registered candidate'}; fingerprint `{(inc.get('fingerprint') or '?')[:16]}`); first seen in the corpus {first_seen}.")
    L.append(f"- Ranked games since first seen: **{len(inc_ranked)}**, W-L-D {data['wld'][0]}-{data['wld'][1]}-{data['wld'][2]}; score − E {fmt(data['since_activation'])}.")
    L.append(f"- First 40 ranked after first sighting: score − E {fmt(first40)}. Old absolute screen (mean < −0.08 and 95th pct < 0): **{'met' if trigger else 'not met'}** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.")
    L.append(f"- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E {fmt(roll)}{' — **below −0.08 with 95th pct < 0**' if drift_flag else ''}.")
    L.append(f"- Elo now {elo_now} (rank {rank_now}); 24 h ago {data['elo']['h24']}; 7 d ago {data['elo']['d7'] if data['elo']['d7'] is not None else 'n/a (no snapshot)'}.")
    L.append(f"- Unranked games of the incumbent in the window (exposure only, not scored here): {len(unranked_inc)}.\n")
    L.append('## Rosters (ranked, incumbent only)\n')
    L.append('| roster | definition | teams | score − E |')
    L.append('|---|---|---|---|')
    defs = dict(band='teams met in ranked, last 48 h', top='current top ten (non-dev)', style='one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent',
                regression='opponents with ≥ 5 ranked games and mean score − E > 0')
    for k, v in rosters.items():
        L.append(f"| {k} | {defs[k]} | {len(v)}: {', '.join(map(str, v[:20]))}{' …' if len(v) > 20 else ''} | {fmt(roster_stats[k])} |")
    L.append('\n## Per map (ranked, incumbent)\n')
    L.append('Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, '
             'Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.\n')
    L.append('| map | score − E |')
    L.append('|---|---|')
    for m, b in sorted(((m, b) for m, b in data['by_map'].items() if ' · ' not in m), key=lambda kv: kv[1]['mean']):
        L.append(f'| {m} | {fmt(b)} |')
        for v, bv in sorted((k, x) for k, x in data['by_map'].items() if k.startswith(m + ' · ')):
            L.append(f'| ↳ {v.split(" · ", 1)[1]} | {fmt(bv)} |')
    L.append('\n## Drift (all our ranked games)\n')
    L.append(f"- Last 7 days: {fmt(this_week)}; the 7 days before: {fmt(prev_week)}.")
    for b, v in sorted(data['by_bot'].items(), key=lambda kv: -kv[1]['n']):
        L.append(f"- submission {b}: {fmt(v)}")
    L.append('\n## Errors and timeouts\n')
    L.append('- Not yet measured for ranked games (needs a replay-side fault read; the hub verifies faults only for games it requests). Requested battles report faults per job in `hub-state/battles/`.')
    L.append(f"- Ranked games without an Elo expectation (no snapshot): {data['missing_expectation']}.\n")
    (repo / a.out).parent.mkdir(parents=True, exist_ok=True)
    (repo / a.out).write_text('\n'.join(L) + '\n')
    print(json.dumps({k: data[k] for k in ('active', 'incumbent', 'ranked_since', 'since_activation', 'first40', 'rolling40', 'rollback_trigger', 'drift_flag', 'elo')}, default=str))


if __name__ == '__main__':
    main()
