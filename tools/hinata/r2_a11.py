"""Hinata — D-069 §C arm A11: encoder + HB-1 vector WITHOUT hb_p (one model; A5's inputs minus hb_pF/hb_pR/hb_pL). A measurement
arm (descriptive in r2_inventory.json; selection by accuracy suspended, D-068). Recipe = r2_battery.fit for arm A5 (r2_bc.PARAMS,
series5 folds, dev120 oracle F/R/L rows, 400 and 800 rounds from one fit) with A5's column list filtered; outputs renamed
A5-* -> A11-* (registry and p files). Fixed in P-hinata-03 §"Arm A11" before the fit. TRAINING-SPLIT ROWS ONLY.

  python3 tools/hinata/r2_a11.py --rows <p0,p1> --side <hb shards,...> --run build/hinata/r2/battery/A11-u [--expect-folds ...]
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2_battery as BAT  # noqa: E402
import r2_bc as R  # noqa: E402

_cols = BAT.cols


def cols(arm, enc, hbf):
    c = _cols(arm, enc, hbf)
    return [x for x in c if x not in BAT.HBP] if arm == 'A5' else c


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--rows', required=True); ap.add_argument('--side', required=True)
    ap.add_argument('--run', required=True); ap.add_argument('--expect-folds'); ap.add_argument('--sizes', default='400,800')
    ap.add_argument('--teachers', default='build/learn/kageyama/teachers_v1.parquet'); ap.add_argument('--features', default=str(R.FEATS))
    ap.add_argument('--budget', type=float, default=1e9)
    a = ap.parse_args()
    ns = argparse.Namespace(cmd='fit', arm='A5', rows=a.rows, side=a.side, teachers=a.teachers, features=a.features, hb_prefix='hb_f_',
                            run=a.run, sizes=a.sizes, weighted=False, budget=a.budget, expect_folds=a.expect_folds)
    BAT.cols = cols; BAT.fit(ns); run = Path(a.run)
    if not (run / 'registry.json').exists():
        print('no registry (budget reached?); rerun to resume'); return
    reg = json.loads((run / 'registry.json').read_text())
    for n in list(reg['arms']):
        if not n.startswith('A5-'):
            continue
        t = n.replace('A5-', 'A11-'); (run / f'p_{n}.npy').rename(run / f'p_{t}.npy'); reg['arms'][t] = reg['arms'].pop(n)
    reg['info']['model_bytes'] = {k.replace('A5-', 'A11-'): v for k, v in reg['info']['model_bytes'].items()}
    reg['artifact'] = 'hinata-r2-battery-A11'; reg['info']['a11'] = dict(dropped='hb_pF, hb_pR, hb_pL', wrapper_sha=R.sha(__file__))
    (run / 'registry.json').write_text(json.dumps(reg, indent=1, default=str)); print({k: v['frl_all']['acc'] for k, v in reg['arms'].items()})


if __name__ == '__main__':
    main()
