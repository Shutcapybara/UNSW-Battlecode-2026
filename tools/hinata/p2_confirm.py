"""P-2 (hinata-v0b) one-shot held-out confirmation — Tanaka review §4, D-051 §6. Nothing here runs without a Chair record.

  manifest  --out build/hinata/p2/population.parquet      # held-out population from manifest v2; reads NO outcome column
  selftest                                                  # the whole scorer on the frozen DEVELOPMENT OOF (no held-out map)
  run       --gate-spec <json> --population <parquet>       # ONE SHOT: atomic claim -> predict -> seal predictions
  score     --claim build/hinata/p2/CLAIM.json              # deterministic metrics + gate from the sealed predictions only

Frozen inputs (hash-checked): source tools/hinata/archive/v0_2920bb57.py (reproduces fit-lq bit for bit, PROVENANCE-P2.md),
V0b weights build/hinata/v0/fit-lq/v0b_*.json (4 dp, as frozen), Φ comparator build/hinata/v0/fit-lq-phi/phi_*.json (fitted
on the frozen rows c958e8c7…, never refitted on new data). Population: post-m2, in_scope, Autarky/Maze/Trauma, decoded at
manifest time; columns `ranked`, `clean` (series has no P-2 game, v2 `consumed_by`). Rows: side A, checkpoint rows of games
still running (ended rows dropped), decisive games only — the estimand conditions on the game still running.
Intervals: paired whole-series percentile bootstrap, B = 1000, seed 7, numpy 'linear' percentiles; ONE series draw per
replicate shared by every cell, both models and every population column (series resampled together across checkpoints).
Gate: read from the spec (Chair's D-052); a declared cell that is absent, has one outcome class, or has a missing model
file makes the verdict INCOMPLETE. The receipt is written at every stage; a failed run keeps its receipt and the CLAIM
blocks any second run.
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path.cwd(); P2 = ROOT / 'build/hinata/p2'
SRC = ROOT / 'tools/hinata/archive/v0_2920bb57.py'; SRC_SHA = '2920bb5746c41cacacab2d11c84fe99d3f69ad784e3fa3743f8795ccc1fdfa3f'
V0B = ROOT / 'build/hinata/v0/fit-lq'; PHI = ROOT / 'build/hinata/v0/fit-lq-phi'
SPLITS = ROOT / 'build/learn/splits/games_split_v2.parquet'; HELDOUT = ROOT / 'docs/learning/splits/heldout-maps.json'
CPS = (10, 25, 50, 100, 150, 250, 400); B, SEED = 1000, 7
CELLS = [('post-m2', 'elim', c) for c in CPS] + [('post-m2', 'rl', c) for c in CPS]
POPS = {'ranked_clean': lambda x: x.ranked & x.clean, 'ranked': lambda x: x.ranked, 'unranked': lambda x: ~x.ranked,
        'all_clean': lambda x: x.clean, 'all': lambda x: x.ranked | ~x.ranked}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def v0mod():
    assert sha(SRC) == SRC_SHA, 'archived source changed'
    s = importlib.util.spec_from_file_location('v0_frozen', SRC); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    m.MODEL = 'lr_q'; return m


def weights():
    w = {}
    for era, reg, cp in CELLS:
        fv, fp = V0B / f'v0b_{era}_{reg}_r{cp}.json', PHI / f'phi_{era}_{reg}_r{cp}.json'
        w[(era, reg, cp)] = (json.loads(fv.read_text()) if fv.exists() else None, json.loads(fp.read_text()) if fp.exists() else None)
    h = {f.name: sha(f) for f in sorted(list(V0B.glob('v0b_*.json')) + list(PHI.glob('phi_*.json')))}
    return w, h


def predict(m, x, wv, wp):
    sig = lambda z: 1 / (1 + np.exp(-z))
    xq = m.prep_lq(x)
    pv = sig((xq[m.LQ].to_numpy(float) - 0.5) @ np.array([wv[k] for k in m.LQ]))
    pp = sig((x[m.PHI].to_numpy(float) - 0.5) @ np.array([wp[k] for k in m.PHI]))
    return pv, pp


# ---------- fast weighted metrics, vectorised over bootstrap replicates ----------
def wauc(y, p, W):
    """AUC with replicate weights W (R x n); ties count 1/2. Equals the AUC of the replicated sample."""
    o = np.argsort(p, kind='mergesort'); y, p, W = y[o], p[o], W[:, o]
    _, start = np.unique(p, return_index=True); grp = np.repeat(np.arange(len(start)), np.diff(np.append(start, len(p))))
    Wn, Wp = W * (y == 0), W * (y == 1)
    gn = np.zeros((W.shape[0], len(start))); np.add.at(gn.T, grp, Wn.T)
    below = np.cumsum(gn, 1) - gn                                     # negatives strictly below each tie group
    num = (Wp * (below[:, grp] + 0.5 * gn[:, grp])).sum(1); den = Wp.sum(1) * Wn.sum(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where(den > 0, num / den, np.nan)


def wslope(y, p, W, it=30):
    """Weighted logistic recalibration y ~ a + b·logit(p) by vectorised IRLS; returns (a, b) per replicate."""
    p = np.clip(p, 1e-4, 1 - 1e-4); z = np.log(p / (1 - p)); R = W.shape[0]; ab = np.zeros((R, 2)); ab[:, 1] = 1
    for _ in range(it):
        eta = ab[:, :1] + ab[:, 1:] * z; mu = 1 / (1 + np.exp(-eta)); v = W * mu * (1 - mu) + 1e-12; r = W * (y - mu)
        g = np.stack([r.sum(1), (r * z).sum(1)], 1)
        H = np.stack([np.stack([v.sum(1), (v * z).sum(1)], 1), np.stack([(v * z).sum(1), (v * z * z).sum(1)], 1)], 1)
        ab = ab + np.linalg.solve(H, g[..., None])[..., 0]
    return ab


def wbrier(y, p, W):
    return (W * (p - y) ** 2).sum(1) / W.sum(1)


def pct(a):
    a = a[~np.isnan(a)]
    return [float(np.percentile(a, 5)), float(np.percentile(a, 95))] if len(a) else [None, None]


def evaluate(pred, spec):
    """pred: one row per (game, cell) with y, p_v, p_phi, map, series_key, ranked, clean. Deterministic."""
    sk, inv = np.unique(pred.series_key.astype(str), return_inverse=True); pred = pred.assign(_s=inv)
    rng = np.random.default_rng(SEED); C = np.stack([np.bincount(rng.integers(0, len(sk), len(sk)), minlength=len(sk)) for _ in range(B)])
    out = []
    for pop, f in POPS.items():
        for era, reg, cp in CELLS:
            x = pred[(pred.map_era == era) & (pred.regime == reg) & (pred['round'] == cp) & f(pred)]
            r = dict(population=pop, map_era=era, regime=reg, round=cp, n=len(x), pos=int(x.y.sum()), neg=int(len(x) - x.y.sum()),
                     series=int(x._s.nunique()), maps=sorted(x['map'].unique()))
            if r['pos'] == 0 or r['neg'] == 0:
                r['status'] = 'UNDEFINED'; out.append(r); continue
            y = x.y.to_numpy(float); W1 = np.ones((1, len(x))); Wb = C[:, x._s.to_numpy()].astype(float)
            for k, col in (('v', 'p_v'), ('phi', 'p_phi')):
                p = x[col].to_numpy(float)
                r[f'auc_{k}'] = float(wauc(y, p, W1)[0]); ab = wslope(y, p, W1)[0]; r[f'int_{k}'], r[f'slope_{k}'] = float(ab[0]), float(ab[1])
                r[f'brier_{k}'] = float(wbrier(y, p, W1)[0]); r[f'_a_{k}'] = wauc(y, p, Wb); abb = wslope(y, p, Wb)
                r[f'slope_{k}_ci'], r[f'int_{k}_ci'] = pct(abb[:, 1]), pct(abb[:, 0])
            r['d_auc'] = r['auc_v'] - r['auc_phi']; r['d_auc_ci'] = pct(r.pop('_a_v') - r.pop('_a_phi'))
            r['per_map'] = {m: dict(n=int(len(g)), auc_v=float(wauc(g.y.to_numpy(float), g.p_v.to_numpy(float), np.ones((1, len(g))))[0]),
                                    auc_phi=float(wauc(g.y.to_numpy(float), g.p_phi.to_numpy(float), np.ones((1, len(g))))[0]))
                            for m, g in x.groupby('map') if 0 < g.y.sum() < len(g)}
            r['status'] = 'OK'; out.append(r)
    return out, gate(out, spec)


def gate(rows, spec):
    """Spec keys (all from the Chair's record): binding_population, report_only_cells ["rl/r10", ...], min_lb_all,
    late_rl_rounds, min_lb_late, slope_from_round, slope_tol, rl50_min_auc, rl50_population."""
    why, inc = [], []
    T = {(r['population'], r['regime'], r['round']): r for r in rows}
    bp = spec['binding_population']; ro = set(spec.get('report_only_cells', []))
    for era, reg, cp in CELLS:
        if f'{reg}/r{cp}' in ro:
            continue
        r = T.get((bp, reg, cp))
        if r is None or r['status'] != 'OK':
            inc.append(f'{bp}/{reg}/r{cp}: {"absent" if r is None else r["status"]}'); continue
        lb = r['d_auc_ci'][0]
        if lb is None or lb <= spec['min_lb_all']:
            why.append(f'{reg}/r{cp}: ΔAUC 5th pct {lb} ≤ {spec["min_lb_all"]}')
        if reg == 'rl' and cp in spec['late_rl_rounds'] and (lb is None or lb <= spec['min_lb_late']):
            why.append(f'rl/r{cp}: ΔAUC 5th pct {lb} ≤ {spec["min_lb_late"]}')
        if cp >= spec['slope_from_round'] and abs(r['slope_v'] - 1) > abs(r['slope_phi'] - 1) + spec['slope_tol']:
            why.append(f'{reg}/r{cp}: |slope_V−1| {abs(r["slope_v"] - 1):.3f} > |slope_Φ−1| {abs(r["slope_phi"] - 1):.3f} + {spec["slope_tol"]}')
    r = T.get((spec['rl50_population'], 'rl', 50))
    if r is None or r['status'] != 'OK':
        inc.append(f'{spec["rl50_population"]}/rl/r50 absent')
    elif r['auc_v'] < spec['rl50_min_auc'] or r['auc_v'] < r['auc_phi']:
        why.append(f'rl/r50 AUC_V {r["auc_v"]:.4f} vs min {spec["rl50_min_auc"]} and AUC_Φ {r["auc_phi"]:.4f}')
    verdict = 'INCOMPLETE' if inc else ('PASS' if not why else 'FAIL')
    return dict(verdict=verdict, incomplete=inc, reasons=why)


def receipt(path, **kw):
    j = json.loads(path.read_text()) if path.exists() else {}
    j.setdefault('stages', []).append(dict(at=time.strftime('%FT%TZ', time.gmtime()), **kw)); path.write_text(json.dumps(j, indent=1, default=str))


def cmd_manifest(a):
    import duckdb
    hm = json.loads(HELDOUT.read_text())['heldout_maps']; assert sorted(hm) == ['Autarky', 'Maze', 'Trauma']
    q = ','.join(f"'{m}'" for m in hm)
    g = duckdb.sql(f"""select game, series_key, map, ranked, consumed_by from read_parquet('{SPLITS}')
                       where split = 'heldout_map' and map_era = 'post-m2' and in_scope and map in ({q})""").df()
    dec = duckdb.sql(f"select distinct game from read_parquet('{ROOT}/build/s1/corpus/series/part-*.parquet', union_by_name=true)"
                     f" where game in (select game from g)").df()
    sc = g.groupby('series_key').consumed_by.apply(lambda s: (s != '').any()); g['clean'] = ~g.series_key.map(sc)
    g['decoded'] = g.game.isin(dec.game); out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    g = g.drop(columns='consumed_by').sort_values('game').reset_index(drop=True); g.to_parquet(out)
    meta = dict(file=str(out), sha256=sha(out), splits_v2_sha=sha(SPLITS), heldout_sha=sha(HELDOUT), written=time.strftime('%FT%TZ', time.gmtime()),
                counts=g.groupby(['map', 'ranked', 'clean', 'decoded']).size().rename('games').reset_index().to_dict('records'),
                note='No outcome column read (games_split_v2 has none; series parts read for game ids only).')
    Path(str(out) + '.json').write_text(json.dumps(meta, indent=1, default=str)); print(json.dumps(meta, indent=1, default=str))


def cmd_selftest(a):
    """Development OOF from fit-lq stands in for predictions: checks plumbing and the bootstrap against Tanaka's table."""
    oof = pd.read_parquet(V0B / 'oof.parquet'); tr = pd.read_parquet(V0B / 'train_rows.parquet')[['game', 'series_id', 'ranked']].drop_duplicates('game')
    x = oof.merge(tr, on='game', validate='many_to_one').rename(columns={'p_v0': 'p_v', 'series_id': 'series_key'})
    x['round'] = x['round'].astype(int); x['clean'] = True
    spec = json.loads(Path(a.gate_spec).read_text()) if a.gate_spec else DEFAULT_SPEC
    t0 = time.time(); rows, g = evaluate(x, spec)
    keep = [r for r in rows if r['population'] == 'all' and r['status'] == 'OK']
    print(pd.DataFrame([{k: r[k] for k in ('regime', 'round', 'n', 'series', 'auc_v', 'auc_phi', 'd_auc', 'd_auc_ci', 'slope_v', 'slope_phi')} for r in keep]).round(5).to_string(index=False))
    print('SELFTEST gate (development OOF, NOT a confirmation):', g, f'{time.time() - t0:.0f}s')
    P2.mkdir(parents=True, exist_ok=True); (P2 / 'selftest.json').write_text(json.dumps(dict(rows=rows, gate=g), indent=1, default=str))


DEFAULT_SPEC = dict(binding_population='all', report_only_cells=[], min_lb_all=-0.01, late_rl_rounds=[150, 250, 400], min_lb_late=0.0,
                    slope_from_round=25, slope_tol=0.05, rl50_min_auc=0.66, rl50_population='all', record='SELFTEST')


def cmd_run(a):
    spec = json.loads(Path(a.gate_spec).read_text())
    for k in ('record', 'binding_population', 'min_lb_all', 'late_rl_rounds', 'min_lb_late', 'slope_from_round', 'slope_tol', 'rl50_min_auc', 'rl50_population'):
        assert k in spec, f'gate spec lacks {k}'
    assert spec['record'].startswith('D-'), 'gate spec must name the Chair record that froze it'
    pop = pd.read_parquet(a.population); meta = json.loads(Path(a.population + '.json').read_text()); assert sha(a.population) == meta['sha256']
    m = v0mod(); w, wh = weights()
    missing = [c for c, (wv, wp) in w.items() if wv is None or wp is None]
    P2.mkdir(parents=True, exist_ok=True); claim = P2 / 'CLAIM.json'
    fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)          # atomic one-shot: a second run fails here
    os.write(fd, json.dumps(dict(claimed=time.strftime('%FT%TZ', time.gmtime()), spec=spec, spec_sha=sha(a.gate_spec), population_sha=meta['sha256'],
                                 source_sha=SRC_SHA, weight_files=wh, missing_cells=missing, B=B, seed=SEED), indent=1).encode()); os.close(fd)
    rc = P2 / 'RECEIPT.json'
    try:
        receipt(rc, stage='claimed', claim_sha=sha(claim))
        hm = json.loads(HELDOUT.read_text())['heldout_maps']
        d = m.load(['post-m2'], maps=hm); d = d[(d.side == 'A') & d.game.isin(pop.game[pop.decoded])]
        d = d.merge(pop[['game', 'series_key', 'ranked', 'clean']].rename(columns={'ranked': 'ranked_m'}), on='game', validate='many_to_one')
        d['ranked'] = d.pop('ranked_m').astype(bool); d['round'] = d['round'].astype(int); parts = []
        for (era, reg, cp), x in d.groupby(['map_era', 'regime', 'round']):
            wv, wp = w.get((era, reg, cp), (None, None))
            if wv is None or wp is None:
                continue
            pv, pp = predict(m, x, wv, wp)
            parts.append(x[['game', 'series_key', 'map', 'map_era', 'regime', 'round', 'ranked', 'clean', 'y']].assign(p_v=pv, p_phi=pp))
        pred = pd.concat(parts, ignore_index=True); pf = P2 / 'predictions.parquet'; pred.to_parquet(pf); os.chmod(pf, 0o444)
        receipt(rc, stage='sealed', predictions_sha=sha(pf), rows=len(pred), games=int(pred.game.nunique()))
        print('sealed', pf, sha(pf)); print('now: p2_confirm.py score')
    except BaseException as e:
        receipt(rc, stage='error', error=repr(e)); raise


def cmd_score(a):
    claim = json.loads((P2 / 'CLAIM.json').read_text()); rc = json.loads((P2 / 'RECEIPT.json').read_text())
    sealed = [s for s in rc['stages'] if s['stage'] == 'sealed']; assert sealed, 'no sealed predictions'
    pf = P2 / 'predictions.parquet'; assert sha(pf) == sealed[0]['predictions_sha'], 'predictions changed after sealing'
    rows, g = evaluate(pd.read_parquet(pf), claim['spec'])
    if claim['missing_cells']:
        g['verdict'] = 'INCOMPLETE'; g['incomplete'] += [f'model file missing: {c}' for c in claim['missing_cells']]
    res = P2 / 'result.json'; res.write_text(json.dumps(dict(gate=g, rows=rows), indent=1, default=str))
    receipt(P2 / 'RECEIPT.json', stage='scored', verdict=g['verdict'], result_sha=sha(res)); print(json.dumps(g, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['manifest', 'selftest', 'run', 'score'])
    ap.add_argument('--out', default='build/hinata/p2/population.parquet'); ap.add_argument('--gate-spec'); ap.add_argument('--population')
    a = ap.parse_args(); dict(manifest=cmd_manifest, selftest=cmd_selftest, run=cmd_run, score=cmd_score)[a.cmd](a)
