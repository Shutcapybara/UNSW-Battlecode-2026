"""Python (LightGBM) against C++ (export_gbt.py header + cpp/gbt_compact.hpp) prediction parity on development rows
(Data lane, kageyama; D-065 §D). Rows: oracle move rows of a teacher-row parquet (train split only), sampled.
    python gbt_parity.py MODEL.txt HEADER.hpp NS FEATURES.txt ROWS.parquet [N] [OUT.json]"""
import json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb

model, header, ns, feats, rows = sys.argv[1:6]
n = int(sys.argv[6]) if len(sys.argv) > 6 else 20000
cols = [l.strip() for l in open(feats) if l.strip()]
D = pd.read_parquet(rows, columns=['blocks_src', 'y_kind', 'split'] + cols)
assert (D.split == 'train').all()
D = D[(D.blocks_src == 'oracle') & (D.y_kind == 0)]
D = D.sample(min(n, len(D)), random_state=7)
X = D[cols].to_numpy(np.float32)
P = lgb.Booster(model_file=model).predict(X)
here = Path(__file__).parent / 'cpp'
with tempfile.TemporaryDirectory() as t:
    exe = f'{t}/par'
    subprocess.run(['g++', '-std=c++20', '-O2', f'-DGBT_HEADER="{Path(header).resolve()}"', f'-DGBT_NS={ns}',
                    f'-I{here}', str(here / 'gbt_parity_main.cpp'), '-o', exe], check=True)
    X.tofile(f'{t}/X.f32')
    subprocess.run([exe, f'{t}/X.f32', f'{t}/P.f64'], check=True)
    C = np.fromfile(f'{t}/P.f64').reshape(len(X), -1)
fr = [0, 1, 3]
a, b = P[:, fr] / P[:, fr].sum(1, keepdims=True), C[:, fr] / C[:, fr].sum(1, keepdims=True)
res = dict(rows=len(X), max_abs_dp=float(np.abs(P - C).max()), argmax_agree=float((P.argmax(1) == C.argmax(1)).mean()),
           frl_max_abs_dp=float(np.abs(a - b).max()), frl_argmax_agree=float((a.argmax(1) == b.argmax(1)).mean()))
print(json.dumps(res))
if len(sys.argv) > 7:
    Path(sys.argv[7]).write_text(json.dumps(res, indent=1))
