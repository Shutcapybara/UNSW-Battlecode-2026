"""Queen / endgame reading of a tester's panel arms, paired by fixture, with the engine's verdict as the outcome.

  python3 tools/antioch/panel_reading.py extract --runs ../wt-carthage/build/carthage/runs --arms carthage-00-base,carthage-06-queen-avoid \
      --out build/antioch/panel_queen.parquet --jobs 6
  python3 tools/antioch/panel_reading.py report build/antioch/panel_queen.parquet --base carthage-00-base

Replay names are s<seed>__<map>__<botA>__<botB>.replay (run_panel). The fixture key is (panel, seed, map, opponent, seat), so
an arm's game pairs with the base's game on the same fixture. Win is the engine's (GameResult), not frame.decode's old-rule
inference. Report: per panel, the paired win change split by how the base game ended (round limit vs elimination) and by
pocket maps, with a fixture-bootstrap 90 % interval, plus queen survival in round-limit games and queen-decided W/L.
"""
import argparse, glob, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
POCKET = {'slithery_fight', 'autarky', 'dilemma', 'dilemma_10'}


def _job(args):
    path, arm, panel = args
    from tools.antioch.queen import rows_for
    stem = Path(path).stem
    parts = stem.split('__')
    if len(parts) != 4:
        return []
    seed, mp, a, b = parts
    me = 'A' if a == arm else 'B' if b == arm else None
    if me is None:
        return []
    rows = rows_for(path, gid=stem)
    out = []
    for r in rows:
        if r.get('side') != me:
            continue
        r.update(arm=arm, panel=panel, seed=seed, map=mp, opp=b if me == 'A' else a, seat=me,
                 fixture=f'{panel}|{seed}|{mp}|{b if me == "A" else a}|{me}')
        out.append(r)
    return out


def extract(a):
    import multiprocessing as mp
    import pandas as pd
    tasks = []
    for arm in a.arms.split(','):
        for panel in ('pool', 'gen'):
            for p in glob.glob(os.path.join(a.runs, arm, panel, 'replays', '*.replay')):
                tasks.append((p, arm, panel))
    with mp.get_context('fork').Pool(a.jobs) as pool:
        rows = [r for rs in pool.imap_unordered(_job, tasks, chunksize=8) for r in rs]
    df = pd.DataFrame(rows)
    if Path(a.out).exists() and not a.replace:
        old = pd.read_parquet(a.out)
        df = pd.concat([old[~old.arm.isin(df.arm.unique())], df])
    df.to_parquet(a.out, index=False)
    print(f'{len(df)} side rows ({len(tasks)} replays) -> {a.out}')


def boot(x, n=2000, seed=0):
    import numpy as np
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    if len(x) == 0:
        return float('nan'), float('nan'), float('nan')
    m = rng.choice(x, (n, len(x))).mean(1)
    return x.mean(), np.quantile(m, 0.05), np.quantile(m, 0.95)


def report(a):
    import pandas as pd
    d = pd.read_parquet(a.path)
    b0 = d[d.arm == a.base]
    early = b0.assign(e=b0.queen_death_round.fillna(999) <= 10).groupby('map').e.mean()
    pocket = set(early[early >= 0.9].index)      # maps where the base's queen dies by r10 in >= 90 % of games
    print('pocket maps (base queen dead by r10 in >= 90 %):', sorted(pocket))
    d['pocket'] = d['map'].isin(pocket)
    base = d[d.arm == a.base].set_index('fixture')
    fmt = lambda t: f'{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]'
    for arm in [x for x in d.arm.unique() if x != a.base]:
        t = d[d.arm == arm].set_index('fixture')
        j = t.join(base, rsuffix='_b', how='inner')
        print(f'\n=== {arm} vs {a.base}  (paired fixtures {len(j)})')
        for panel in ('pool', 'gen'):
            x = j[j.panel == panel]
            dw = x.engine_won - x.engine_won_b
            rl_b = x.end_reason_b == 1
            print(f'  {panel}: n {len(x)}  win {x.engine_won_b.mean():.3f} -> {x.engine_won.mean():.3f}  Δ {fmt(boot(dw))}')
            print(f'     base ended at round limit (n {rl_b.sum()}): Δ {fmt(boot(dw[rl_b]))};  base ended by elimination (n {(~rl_b).sum()}): Δ {fmt(boot(dw[~rl_b]))}')
            np_ = ~x.pocket
            print(f'     non-pocket maps (n {np_.sum()}): Δ {fmt(boot(dw[np_]))};  pocket (n {(~np_).sum()}): Δ {fmt(boot(dw[~np_]))}')
            for lab, s, e in (('arm', '', ''), ('base', '_b', '')):
                rl = x[(x['end_reason' + s] == 1) & ~x.pocket]
                qd = rl[rl['decided_by' + s] == 'queen']
                print(f'     {lab}: RL share {(x["end_reason" + s] == 1).mean():.3f}; non-pocket RL queen alive {rl["queen_alive_end" + s].mean():.3f} (n {len(rl)}); '
                      f'queen-decided W/L {int((qd["engine_won" + s] == 1).sum())}/{int((qd["engine_won" + s] == 0).sum())}; '
                      f'elimination losses {int(((x["end_reason" + s] == 0) & (x["engine_won" + s] == 0)).sum())}')
            flips = x[(x.end_reason_b == 1) & (x.end_reason == 0)]
            print(f'     base RL -> arm elimination: {len(flips)} (arm won {int((flips.engine_won == 1).sum())}); '
                  f'base elimination -> arm RL: {int(((x.end_reason_b == 0) & (x.end_reason == 1)).sum())}')


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    e = sp.add_parser('extract'); e.add_argument('--runs', required=True); e.add_argument('--arms', required=True)
    e.add_argument('--out', required=True); e.add_argument('--jobs', type=int, default=4); e.add_argument('--replace', action='store_true')
    r = sp.add_parser('report'); r.add_argument('path'); r.add_argument('--base', required=True)
    a = ap.parse_args()
    extract(a) if a.cmd == 'extract' else report(a)


if __name__ == '__main__':
    main()
