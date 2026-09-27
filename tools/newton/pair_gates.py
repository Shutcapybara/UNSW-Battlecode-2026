#!/usr/bin/env python3
"""Pair a newton arm run's fixtures against the frozen x01 gate records.
Usage: pair_gates.py <run_dir> [--gate screen|compact|gauntlet|reserve]"""
import csv, sys, os, json

GATES = {
 'screen':   'experiment_data/f12-sizematch_20260926143914278071/games.csv',
 'compact':  'experiment_data/fafnir-v01-phalanx_20260926225920357152/games.csv',
 'gauntlet': 'experiment_data/f12-sizematch_20260926144850071036/games.csv',
 'reserve':  'experiment_data/fafnir-v01-release_20260926150818154880/games.csv',
}

def load(path):
    out = {}
    for r in csv.DictReader(open(path)):
        out[(r['opponent'], r['map'], r['side'])] = r
    return out

def main(run_dir, gate):
    base = load(GATES[gate])
    arm = load(os.path.join(run_dir, 'games.csv'))
    aw = al = bw = bl = 0
    per_map = {}
    flips_w, flips_l = [], []
    for k, r in arm.items():
        b = base.get(k)
        if b is None:
            continue
        a_win = r['outcome'] == r['side']
        b_win = b['outcome'] == b['side']
        aw += a_win; al += (not a_win); bw += b_win; bl += (not b_win)
        m = per_map.setdefault(k[1], [0,0,0,0])
        m[0] += a_win; m[1] += (not a_win); m[2] += b_win; m[3] += (not b_win)
        (flips_w if (a_win and not b_win) else (flips_l if (b_win and not a_win) else [])).append('/'.join((k[1],k[2],k[0].split('-')[0])))
    n = aw + al
    print(f"{os.path.basename(run_dir)} [{gate}] arm {aw}-{al} of {n} | x01 same fixtures {bw}-{bl} | delta {aw-bw:+d}")
    for m, (a1,a2,b1,b2) in sorted(per_map.items()):
        flag = ' <<<' if a1 - b1 <= -2 else ''
        print(f"    {m:16s} arm {a1}-{a2}  x01 {b1}-{b2}  delta {a1-b1:+d}{flag}")
    if flips_w: print("    won :", flips_w)
    if flips_l: print("    lost:", flips_l)

if __name__ == '__main__':
    gate = 'compact'
    dirs = []
    for a in sys.argv[1:]:
        if a.startswith('--gate'): gate = a.split('=')[1]
        else: dirs.append(a)
    for d in dirs:
        main(d, gate)
