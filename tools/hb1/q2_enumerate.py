"""HB-1 Q2: where would a free policy's choice be invalid, and what does Heartbreaker do there?

    .venv/bin/python tools/hb1/q2_enumerate.py [--jobs N] [--set corpus|era]

Per actor-turn: state class (ordinary exits / portal exits / split-eligible) x what they did (split, or the
first step's target: free / portal / wall / own / ally / enemy body / enemy head). Also split-size validity.
Writes game_stats/runs/hb1-q2-enumerate-<set>.json.
"""
import argparse, glob, json
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / 'build' / 'hb1'
COLS = ['round', 'length', 'units', 'unit_limit', 'split_elig', 'n_exit_ord', 'n_exit_portal', 'y_family', 'y_first',
        'y_child', 'post_died', 'post_reason'] + [f'c{r}_{k}' for r in 'FRLB' for k in ('block', 'portal')]
TARGET = {0: 'free', 1: 'wall', 2: 'own', 3: 'own', 4: 'ally', 5: 'ally', 6: 'enemy', 7: 'enemyHead'}


def target(block, portal):
    if block == -1:
        return 'portal' if portal else 'edge'
    return TARGET.get(int(block), f'code{block}')


def one(path):
    d = pd.read_parquet(path, columns=COLS)
    st = np.where(d.n_exit_ord > 0, 'ord', np.where(d.n_exit_portal > 0, 'portalOnly', 'none'))
    st = pd.Series(st) + np.where(d.split_elig == 1, '+elig', '-elig')
    act = pd.Series('split', index=d.index)
    mv = d.y_family == 'move'
    for r in 'FRL':
        m = mv & (d.y_first == r)
        act[m] = [target(b, p) for b, p in zip(d.loc[m, f'c{r}_block'], d.loc[m, f'c{r}_portal'])]
    out = pd.crosstab(st.values, act.values)
    # alternatives available in exit-less states: which non-free targets were on offer
    none = (d.n_exit_ord == 0) & (d.n_exit_portal == 0) & (d.split_elig == 0)
    offer = {}
    for i in np.flatnonzero(none.to_numpy()):
        opts = tuple(sorted(target(d[f'c{r}_block'].iat[i], d[f'c{r}_portal'].iat[i]) for r in 'FRL'))
        key = '|'.join(opts) + ' -> ' + act.iat[i]
        offer[key] = offer.get(key, 0) + 1
    sp = d[d.y_family == 'split']
    bad_split = int(((sp.y_child < 2) | (sp.length - sp.y_child < 2) | (sp.units >= sp.unit_limit)).sum())
    died = pd.crosstab(act.values, d.post_reason.values)
    return out, offer, bad_split, len(sp), died


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=14)
    ap.add_argument('--set', default='corpus')
    a = ap.parse_args()
    fs = sorted(glob.glob(str(B / 'v5' / a.set / '*.parquet')))
    tab, offer, bad, nsp, died = None, {}, 0, 0, None
    with Pool(a.jobs) as p:
        for o, of, b, n, dd in p.imap_unordered(one, fs, chunksize=4):
            tab = o if tab is None else tab.add(o, fill_value=0)
            died = dd if died is None else died.add(dd, fill_value=0)
            for k, v in of.items():
                offer[k] = offer.get(k, 0) + v
            bad += b; nsp += n
    tab = tab.fillna(0).astype(int)
    died = died.fillna(0).astype(int)
    pd.set_option('display.width', 200)
    print(tab)
    print('\nexit-less, split-ineligible: options F|R|L -> chosen (top 25)')
    for k, v in sorted(offer.items(), key=lambda kv: -kv[1])[:25]:
        print(f'{v:7d}  {k}')
    print(f'\ninvalid split sizes / capacity: {bad} of {nsp} splits')
    print('\naction target x own death reason\n', died)
    res = dict(set=a.set, games=len(fs), state_x_action=tab.to_dict(), exitless_offers=offer, invalid_splits=bad,
               splits=nsp, target_x_death=died.to_dict())
    (ROOT / 'game_stats' / 'runs' / f'hb1-q2-enumerate-{a.set}.json').write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
