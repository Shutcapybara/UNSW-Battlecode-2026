"""Replay-drive the live games of one source against its local bot within a time budget (Q8), smallest games first.

    python -m tools.analysis.replay_drive_live SUBMISSION BOTDIR BUDGET_SECONDS [MAX_TURNS] [--state LIVE/state/state.json]
    WV=all python -m tools.analysis.replay_drive_live ...   # message-drop variant (replay_drive_msgvar.py)

Outputs `build/replay_drive_live/{full,nomsg_<WV>}_<game>.json`; re-runs skip games already done. Summarise with
`--summary`, which writes `build/a1_replay_drive_live.csv` (agreement, first mismatch round, message-drop agreement).
"""
import csv
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIVE = Path(os.environ.get('JKS_LIVE') or '/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation')
OUT = REPO / 'build' / 'replay_drive_live'


def games_of(state, sub, max_turns):
    return sorted((r['turns'], gid) for gid, r in state['results'].items()
                  if r.get('verified') and r['submission'] == sub and r.get('origin') == 'controlled' and r['side'] == 'A' and r['turns'] <= max_turns)


def drive(sub, botdir, budget, max_turns, state):
    variant = os.environ.get('WV')
    tool = 'replay_drive_msgvar.py' if variant else 'replay_drive.py'
    prefix = f'nomsg_{variant}_' if variant else 'full_'
    OUT.mkdir(parents=True, exist_ok=True)
    t0, done = time.time(), 0
    for turns, gid in games_of(state, sub, max_turns):
        o = OUT / f'{prefix}{gid}.json'
        if o.exists() or time.time() - t0 + turns / 400 > budget:
            continue
        subprocess.run([sys.executable, str(REPO / 'tools/team_recon_claude' / tool), str(LIVE / 'state/decoded' / f'{gid}.replay'), 'A', str(REPO / botdir), str(o)],
                       cwd=REPO, timeout=max(30, budget - (time.time() - t0)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        done += 1
    print('done', done, 'elapsed', round(time.time() - t0))


def summary(state):
    rows = []
    for f in sorted(glob.glob(str(OUT / 'full_*.json'))):
        gid = Path(f).stem[5:]
        d = json.load(open(f))
        st = d.get('stats') or {}
        match, mismatch = st.get('match', 0), st.get('mismatch', 0)
        r = state['results'][gid]
        nm = OUT / f'nomsg_all_{gid}.json'
        dn = json.load(open(nm)) if nm.exists() else None
        rows.append(dict(game=gid, source=r['submission'], map=r['map_name'], opponent=r['opponent'], rounds=r['rounds'], turns=r['turns'], commands=match + mismatch, match=match,
                         mismatch=mismatch, agreement=round(d['agreement'], 4), first_mismatch_round=(d.get('examples') or [{}])[0].get('round'),
                         nomsg_agreement=(round(dn['agreement'], 4) if dn else None), secs=d.get('secs')))
    path = REPO / 'build' / 'a1_replay_drive_live.csv'
    with open(path, 'w') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for sub in sorted({r['source'] for r in rows}):
        rr = [r for r in rows if r['source'] == sub]
        m, x = sum(r['match'] for r in rr), sum(r['mismatch'] for r in rr)
        print(sub, 'games', len(rr), 'commands', m + x, 'agreement', round(m / (m + x), 4), 'exact', sum(1 for r in rr if r['mismatch'] == 0))
    print('wrote', path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    state_path = sys.argv[sys.argv.index('--state') + 1] if '--state' in sys.argv else LIVE / 'state/state.json'
    state = json.load(open(state_path))
    if '--summary' in sys.argv:
        return summary(state)
    sub, botdir, budget = int(args[0]), args[1], float(args[2])
    max_turns = int(args[3]) if len(args) > 3 else 10 ** 9
    drive(sub, botdir, budget, max_turns, state)


if __name__ == '__main__':
    main()
