"""P-2 confirmation prep (D-051 §6; Tanaka review §3). Reads ONLY the frozen development rows (train_rows sha c958e8c7…).

  python3 tools/hinata/p2_prep.py repro   # provenance: does the current tools/hinata/v0.py reproduce fit-lq bit for bit?
  python3 tools/hinata/p2_prep.py phi     # freeze the comparator: Φ fitted on the frozen rows, per cell, full precision

Writes build/hinata/v0/fit-lq-phi/ (never touches build/hinata/v0/fit-lq). No held-out map is loaded; no outcome
outside the 5,799 frozen development games is read.
"""
import hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import v0  # noqa: E402

RUN = Path('build/hinata/v0/fit-lq'); OUT = Path('build/hinata/v0/fit-lq-phi')
FROZEN_ROWS = 'c958e8c7f830c4c5d1b5e322adc44f16152d2a4c4c96714d5d1c30eb091cae76'


def full_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows():
    f = RUN / 'train_rows.parquet'
    assert full_sha(f) == FROZEN_ROWS, 'train_rows.parquet is not the frozen c958e8c7 file'
    d = pd.read_parquet(f)
    assert not set(d['map']) & {'Autarky', 'Maze', 'Trauma'}
    return d


def deps():
    import sklearn, duckdb, lightgbm, pyarrow, platform
    return dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__,
                duckdb=duckdb.__version__, lightgbm=lightgbm.__version__, pyarrow=pyarrow.__version__)


def cmd_repro():
    v0.MODEL = 'lr_q'; d = rows(); rep = dict(v0_sha=full_sha(v0.__file__), registry_code_sha='3138d10777ce5490', deps=deps())
    coef = []
    for (era, reg, cp), xx in d.groupby(['map_era', 'regime', 'round']):
        cp = int(cp)
        xx = v0.prep_lq(xx); m = v0.fit_phi(xx[v0.LQ].to_numpy(float), xx.y.to_numpy(float))
        new = dict(zip(v0.LQ, m.coef_[0].round(4))); old = json.loads((RUN / f'v0b_{era}_{reg}_r{cp}.json').read_text())
        coef.append(dict(cell=f'{era}/{reg}/r{cp}', max_abs_diff=max(abs(new[k] - old[k]) for k in v0.LQ)))
    rep['coef'] = coef
    oof = pd.concat([v0.lomo(d[d['round'] == cp]) for cp in v0.CPS], ignore_index=True)
    ref = pd.read_parquet(RUN / 'oof.parquet')
    k = ['game', 'map', 'map_era', 'regime', 'round']
    j = ref.merge(oof, on=k, suffixes=('_ref', '_new'), how='outer', indicator=True)
    rep['oof'] = dict(rows_ref=len(ref), rows_new=len(oof), unmatched=int((j._merge != 'both').sum()),
                      max_abs_p_v0=float((j.p_v0_ref - j.p_v0_new).abs().max()),
                      max_abs_p_phi=float((j.p_phi_ref - j.p_phi_new).abs().max()))
    OUT.mkdir(parents=True, exist_ok=True); (OUT / 'repro.json').write_text(json.dumps(rep, indent=1, default=str))
    print(json.dumps(rep, indent=1, default=str))


def cmd_phi():
    d = rows(); OUT.mkdir(parents=True, exist_ok=True); cells = {}
    for (era, reg, cp), xx in d.groupby(['map_era', 'regime', 'round']):
        cp = int(cp)
        m = v0.fit_phi(xx[v0.PHI].to_numpy(float), xx.y.to_numpy(float))
        w = {k: float(c) for k, c in zip(v0.PHI, m.coef_[0])}
        cells[f'{era}/{reg}/r{cp}'] = dict(coef=w, n_rows=int(len(xx)), n_games=int(xx.game.nunique()))
        (OUT / f'phi_{era}_{reg}_r{cp}.json').write_text(json.dumps(w))
    reg = dict(artifact='hinata-phi-comparator', for_='P-2 confirmation (D-051 §6)', train_rows_sha=FROZEN_ROWS,
               v0_sha=full_sha(v0.__file__), model='LogisticRegression(C=1.0, fit_intercept=False, max_iter=1000) on Φ six shares − 0.5,'
               ' both sides, running rows; predict p = sigmoid((x − 0.5)·w); full float64 coefficients',
               features=v0.PHI, cells=cells, deps=deps(), written=time.strftime('%FT%TZ', time.gmtime()))
    (OUT / 'registry.json').write_text(json.dumps(reg, indent=1))
    files = sorted(OUT.glob('phi_*.json')); manifest = {f.name: full_sha(f) for f in files}
    (OUT / 'MANIFEST.sha256.json').write_text(json.dumps(manifest, indent=1))
    print(pd.DataFrame({k: v['coef'] for k, v in cells.items()}).T.round(3).to_string())


if __name__ == '__main__':
    dict(repro=cmd_repro, phi=cmd_phi)[sys.argv[1]]()
