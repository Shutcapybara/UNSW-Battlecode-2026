"""HB-1 Q4 fidelity: drive the built mimic binary with the exact round blocks Heartbreaker received in held-out
replays and compare its commands with theirs, per component. One fresh process per dragon (init block + its blocks),
as on the judge; a dragon's process keeps its own memory of its own choices while the boards follow the replay
(open-loop conditional replay, as tools/team_recon_claude/replay_drive.py).

    .venv/bin/python tools/hb1/replay_drive_cpp.py BIN [--games N] [--jobs J] [--out NAME]

BIN is a native build of a bot dir (e.g. g++ -O2 -std=c++20 -I bots/hb1-01-structured bots/hb1-01-structured/main.cpp).
Games: the Q1 held-out corpus games (seed 62), never used for fitting. Writes game_stats/runs/hb1-<NAME>.json.
"""
import argparse, collections, json, subprocess, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'team_recon_claude'))
import recon, roundblock, features_view as FV

LET = {'north': 'N', 'east': 'E', 'south': 'S', 'west': 'W'}


def drive(args):
    binpath, path, side, gid = args
    g = recon.Game(path)
    procs, seen, pend = {}, {}, {}
    st = collections.Counter()

    def spawn(d):
        p = subprocess.Popen([binpath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             text=True, bufsize=1)
        p.stdin.write(f'ID {d.id}\nTEAM {d.team}\nMAP {g.board.W} {g.board.H}\nUNIT_LIMIT {g.board.unit_limit}\n')
        return p

    def ask(p, lines):
        try:
            p.stdin.write('\n'.join(lines) + '\n\n')
            p.stdin.flush()
        except BrokenPipeError:
            return None
        out = []
        while True:
            s = p.stdout.readline()
            if not s:
                return None
            s = s.rstrip('\n')
            if s == 'ENDTURN':
                return out
            out.append(s)

    def finish():
        """Score the pending turn once its action and sonar are known."""
        if 'rec' not in pend:
            return
        mine, msonar = pend['mine'], pend['msonar']
        rec, rsonar, facing = pend['rec'], pend['rsonar'], pend['facing']
        st['turns'] += 1
        if mine is None:
            st['no_reply'] += 1
        elif rec[0] in ('move', 'split'):
            st['family_n'] += 1
            st['family_ok'] += mine[0] == rec[0]
            if rec[0] == 'move' and mine[0] == 'move':
                st['dir_n'] += 1
                st['dir_ok'] += mine[1][0] == rec[1][0]
            if rec[0] == 'split' and mine[0] == 'split':
                st['size_n'] += 1
                st['size_ok'] += mine[1] == rec[1]
            st['cmd_ok'] += (mine[0] == rec[0]) and (mine[1][:1] == rec[1][:1] if rec[0] == 'move' else mine[1] == rec[1])
            if rsonar:
                st['sonar_n'] += 1
                st['sonar_ok'] += sorted(msonar) == sorted(rsonar)
            key = 'split' if rec[0] == 'split' else FV.abs_to_rel(facing, rec[1][0])
            st[f'rec_{key}'] += 1
        pend.clear()

    def cb(kind, **k):
        if kind == 'turn':
            finish()
            d = k['dragon']
            if d.team != side:
                return
            n = seen.get(d.id, 0)
            seen[d.id] = n + 1
            lines = roundblock.build_block(g, d, proto3=(n > 0 or d.parent is not None))
            if d.id not in procs:
                procs[d.id] = spawn(d)
            out = ask(procs[d.id], lines)
            act, sonar = None, []
            for l in out or []:
                q = l.split()
                if q and q[0] == 'MOVE' and len(q) == 2:
                    act = ('move', q[1])
                elif q and q[0] == 'SPLIT' and len(q) == 2:
                    act = ('split', int(q[1]))
                elif q and q[0] == 'SONAR' and len(q) >= 2:
                    sonar.append(q[1])
            pend.update(d=d.id, mine=act, msonar=sonar, rsonar=[], facing=LET[d.facing])
        elif kind == 'action' and pend.get('d') == k['dragon'].id:
            a = k['action']
            if a[0] == 'move':
                pend['rec'] = ('move', ''.join(LET[s] for s in a[1]))
            elif a[0] == 'split':
                pend['rec'] = ('split', int(a[1]))
            else:
                pend['rec'] = (a[0],)
                if a[0] == 'tle':
                    p = procs.pop(k['dragon'].id, None)
                    if p:
                        p.kill()
        elif kind == 'sonar' and pend.get('d') == k['sender'] and 'rec' in pend:
            pend['rsonar'].append(LET[k['direction']])
        elif kind == 'death':
            p = procs.pop(k['dragon'].id, None)
            if p:
                p.kill()

    t0 = time.time()
    g.run(cb)
    finish()
    for p in procs.values():
        p.kill()
    return dict(game=gid, secs=round(time.time() - t0, 1), **st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bin')
    ap.add_argument('--games', type=int, default=40)
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--out', default='q4-fidelity-open')
    a = ap.parse_args()
    gt = pd.read_parquet(ROOT / 'build/hb1/games.parquet')
    games = sorted(gt[gt.set == 'corpus'].game.astype(int))
    test = sorted(np.random.default_rng(62).choice(games, len(games) // 5, replace=False).tolist())
    pick = test[:: max(1, len(test) // a.games)][:a.games]
    gt = gt.set_index('game')
    work = [(str(Path(a.bin).resolve()), gt.loc[g].path, gt.loc[g].side, g) for g in pick]
    rows = []
    with Pool(a.jobs) as pool:
        for r in pool.imap_unordered(drive, work):
            rows.append(r)
            print(json.dumps(r), flush=True)
    d = pd.DataFrame(rows).fillna(0)
    tot = d.sum(numeric_only=True)
    res = dict(games=len(d), turns=int(tot.turns), no_reply=int(tot.get('no_reply', 0)),
               family=tot.family_ok / tot.family_n, direction_given_both_move=tot.dir_ok / tot.dir_n,
               split_size_given_both_split=tot.size_ok / max(1, tot.size_n), command=tot.cmd_ok / tot.family_n,
               sonar_multiset=tot.sonar_ok / max(1, tot.sonar_n),
               recorded_mix={k[4:]: int(tot[k]) for k in tot.index if k.startswith('rec_')}, per_game=rows)
    (ROOT / 'game_stats' / 'runs' / f'hb1-{a.out}.json').write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k != 'per_game'}, indent=1, default=float))


if __name__ == '__main__':
    main()
