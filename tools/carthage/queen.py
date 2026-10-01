#!/usr/bin/env python3
"""Queen statistics for an arm's panel replays (unswbc >= 1.2.3 ranks a timed-out game by queen length first).

The queen is the team's starting dragon: id 0 or 1 (a split child takes a new id; the parent keeps its own). A dead
queen counts 0, so a team whose queen lives beats every team whose queen died at r500, whatever the totals.

    $PY tools/carthage/queen.py ARM [--panel pool|gen|both] [--seeds 1,2,3] [--at 490] [--json OUT]

Per side-game of the arm's bot: queen alive at r<at> (games that end earlier count as dead if our side was
eliminated, and are reported separately if we eliminated the opponent first), queen length at r<at>, whether the queen
is the longest own dragon at r<at> (ties count), queen death round and cause, and the share of r500 games whose
verdict came from the queen term. Per-map table on request (--maps).
"""
from __future__ import annotations

import argparse, glob, json, sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.analysis.features import frame  # noqa: E402

RUNS = ROOT / 'build/carthage/runs'


def one(args):
    path, bot, at = args
    d = frame.load(path, cache_dir=ROOT / 'build/carthage/frames')
    side = 'A' if d['botA'].endswith(bot) else 'B'
    opp = 'B' if side == 'A' else 'A'
    teams = {i: t for i, (t, b) in d['rounds'][0].items()}
    q = {teams[i]: i for i in (0, 1) if i in teams}
    qid, oqid = q.get(side), q.get(opp)
    last = d['last_round']
    death = next((x for x in d['events']['deaths'] if x.get('id') == qid), None)
    snap = d['rounds'][min(at, len(d['rounds']) - 1)]
    own = [len(b) for i, (t, b) in snap.items() if t == side]
    qlen = len(snap[qid][1]) if qid in snap else 0
    oq = len(snap[oqid][1]) if oqid in snap else 0
    stem = Path(path).stem
    return dict(game=stem, map=stem.split('__')[1], seed=int(stem.split('__')[0][1:]), side=side,
                reached=last >= at, winner=d['winner'], reason=d['reason'], won=d['winner'] == side,
                q_alive=qid in snap and last >= at, q_len=qlen if last >= at else 0,
                q_longest=bool(own) and qlen > 0 and qlen >= max(own), own_longest=max(own) if own else 0,
                opp_q_alive=oqid in snap and last >= at, opp_q_len=oq,
                q_death_round=death['round'] if death else None, q_death_cause=death.get('cause') if death else None,
                final_q=d['final'][side].get('queen', 0), final_opp_q=d['final'][opp].get('queen', 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arm'); ap.add_argument('--panel', default='both'); ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--at', type=int, default=490); ap.add_argument('--json'); ap.add_argument('--maps', action='store_true')
    ap.add_argument('--bot', help='bot dir name if it differs from the arm'); ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    aj = RUNS / a.arm / 'pool' / 'arm.json'
    bot = a.bot or (json.load(open(aj)).get('bot', a.arm) if aj.exists() else a.arm)
    seeds = {int(s) for s in a.seeds.split(',')}
    out = {}
    for panel in (['pool', 'gen'] if a.panel == 'both' else [a.panel]):
        reps = [p for p in sorted(glob.glob(str(RUNS / a.arm / panel / 'replays/*.replay')))
                if int(Path(p).stem.split('__')[0][1:]) in seeds]
        if not reps:
            continue
        with ProcessPoolExecutor(a.jobs) as ex:
            rows = list(ex.map(one, [(p, bot, a.at) for p in reps], chunksize=4))
        n = len(rows); R = [r for r in rows if r['reached']]
        s = dict(n=n, reached=len(R), win=sum(r['won'] for r in rows) / n,
                 q_alive=sum(r['q_alive'] for r in R) / max(1, len(R)),
                 q_len_mean=sum(r['q_len'] for r in R) / max(1, len(R)),
                 q_len_alive_mean=sum(r['q_len'] for r in R if r['q_alive']) / max(1, sum(r['q_alive'] for r in R)),
                 q_longest=sum(r['q_longest'] for r in R) / max(1, len(R)),
                 opp_q_alive=sum(r['opp_q_alive'] for r in R) / max(1, len(R)),
                 own_longest_mean=sum(r['own_longest'] for r in R) / max(1, len(R)),
                 reasons=dict(Counter(r['reason'] for r in rows)),
                 queen_decided_won=sum(r['reason'] == 'queen' and r['won'] for r in rows),
                 queen_decided_lost=sum(r['reason'] == 'queen' and not r['won'] and r['winner'] != 'draw' for r in rows),
                 q_death_causes=dict(Counter(r['q_death_cause'] for r in rows if r['q_death_round'] is not None)),
                 q_death_round_median=sorted(r['q_death_round'] for r in rows if r['q_death_round'] is not None)[
                     len([r for r in rows if r['q_death_round'] is not None]) // 2] if any(r['q_death_round'] is not None for r in rows) else None)
        print(f"[{panel}] n={n} reached r{a.at}={len(R)} win={s['win']:.3f} | queen alive@{a.at} {s['q_alive']:.3f} "
              f"len@{a.at} {s['q_len_mean']:.1f} (alive {s['q_len_alive_mean']:.1f}) longest {s['q_longest']:.3f} | "
              f"opp queen alive {s['opp_q_alive']:.3f} | own longest {s['own_longest_mean']:.1f}")
        print(f"  reasons {s['reasons']} queen-decided W/L {s['queen_decided_won']}/{s['queen_decided_lost']}")
        print(f"  queen deaths: median round {s['q_death_round_median']} causes {s['q_death_causes']}")
        if a.maps:
            bym = defaultdict(list)
            for r in rows:
                bym[r['map']].append(r)
            for m, rr in sorted(bym.items()):
                RR = [r for r in rr if r['reached']]
                print(f"  {m:24s} n={len(rr):3d} win={sum(r['won'] for r in rr) / len(rr):.2f} reached={len(RR):3d} "
                      f"qalive={sum(r['q_alive'] for r in RR) / max(1, len(RR)):.2f} qlen={sum(r['q_len'] for r in RR) / max(1, len(RR)):5.1f} "
                      f"qlongest={sum(r['q_longest'] for r in RR) / max(1, len(RR)):.2f} oppq={sum(r['opp_q_alive'] for r in RR) / max(1, len(RR)):.2f}")
        out[panel] = dict(summary=s, rows=rows)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(out))


if __name__ == '__main__':
    main()
