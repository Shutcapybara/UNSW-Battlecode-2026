"""Hinata — D-067 §E.2 arm T0: A1's recipe (HB-1 vector, trees, r2_bc.PARAMS, series5 folds, dev120 oracle rows) WITHOUT HB-1's
time and memory inputs (hb_f_round and every hb_f_mem_*). One fit at 400 and 800 rounds; fixed in P-hinata-03 §"Arm T0" before
the fit. Implemented as r2_battery.fit with A1's column list filtered; outputs renamed A1-* -> T0-* (registry and p files).

  python3 tools/hinata/r2_t0.py --rows <p0,p1> --side <hb shards,...> --run build/hinata/r2/battery/T0-u [--expect-folds ...]
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_battery as BAT  # noqa: E402
import r2_bc as R  # noqa: E402

DROP = lambda c: c == 'hb_f_round' or c.startswith('hb_f_mem_')  # noqa: E731
_cols = BAT.cols


def cols(arm, enc, hbf):
    c = _cols(arm, enc, hbf)
    return [x for x in c if not DROP(x)] if arm == 'A1' else c


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--rows', required=True); ap.add_argument('--side', required=True)
    ap.add_argument('--run', required=True); ap.add_argument('--expect-folds'); ap.add_argument('--sizes', default='400,800')
    ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet'); ap.add_argument('--features', default=str(R.FEATS))
    a = ap.parse_args()
    ns = argparse.Namespace(cmd='fit', arm='A1', rows=a.rows, side=a.side, teachers=a.teachers, features=a.features, hb_prefix='hb_f_',
                            run=a.run, sizes=a.sizes, weighted=False, budget=1e9, expect_folds=a.expect_folds)
    BAT.cols = cols; BAT.fit(ns); run = Path(a.run); reg = json.loads((run / 'registry.json').read_text())
    for n in list(reg['arms']):
        t = n.replace('A1-', 'T0-'); (run / f'p_{n}.npy').rename(run / f'p_{t}.npy'); reg['arms'][t] = reg['arms'].pop(n)
    reg['info']['model_bytes'] = {k.replace('A1-', 'T0-'): v for k, v in reg['info']['model_bytes'].items()}
    reg['artifact'] = 'hinata-r2-battery-T0'; reg['info']['t0'] = dict(dropped='hb_f_round + hb_f_mem_*', wrapper_sha=R.sha(__file__))
    (run / 'registry.json').write_text(json.dumps(reg, indent=1, default=str)); print({k: v['frl_all']['acc'] for k, v in reg['arms'].items()})


if __name__ == '__main__':
    main()
