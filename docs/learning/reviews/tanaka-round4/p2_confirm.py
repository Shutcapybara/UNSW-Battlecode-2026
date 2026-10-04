"""P-2 (hinata-v0b) one-shot held-out confirmation under D-052 §A (gate spec sha 15d79683…) and D-053 §B.

Revision 2 (4 Oct, ~15Z) fixes Tanaka's repair-audit defects at d298a6e7 (reviews/P-2-tanaka-repair-audit.md):
  (1) fail closed on non-finite inputs and metrics: finite labels, predictions and coefficients; every binding point
      metric and interval endpoint finite; valid bootstrap draws >= spec min_valid_draws (990); otherwise INCOMPLETE;
  (2) the score is bound to the claim: CLAIM.json's hash must equal the one recorded at claim time, the scorer's hash
      must equal the audited hash given at claim time, and the gate is re-read from the frozen spec file, whose hash
      must equal D-052's 15d79683…; any mismatch scores INCOMPLETE without evaluating;
  (3) only the exact frozen spec unlocks a claim (sha256 + status FROZEN + record D-052); the PROPOSED spec is refused.
Also reads every D-052 field: min_cell_games (report-only list fixed from outcome-free counts before the claim),
rl50_min_auc_binding (false: AUC_V >= AUC_Phi binds, 0.66 printed), reported_populations, min_coverage_per_map.

  manifest  [--out build/hinata/p2/population.parquet]   # population from manifest v2; reads NO outcome column
  counts                                                 # outcome-free per-cell game counts -> report-only cells
  selftest                                               # whole scorer on the frozen DEVELOPMENT OOF (no held-out map)
  probe                                                  # synthetic defect probes in scratch dirs; no real data
  run --audited-scorer-sha <sha256>                      # ONE SHOT: preflight, atomic claim -> predict -> seal
  score                                                  # verify hashes, then score once

Rows: side A, checkpoint rows of games still running (ended rows dropped), decisive games only. Intervals: paired
whole-series percentile bootstrap, B = 1000, seed 7, numpy 'linear'; ONE series draw per replicate shared by every
cell, both models and every population column. A failed or incomplete run keeps its receipt; the CLAIM blocks a rerun.
"""
import argparse, hashlib, importlib.util, json, math, os, sys, tempfile, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path.cwd(); P2 = ROOT / 'build/hinata/p2'; SELF = Path(__file__).resolve()
S1 = ROOT / 'build/s1/corpus'
SRC = ROOT / 'tools/hinata/archive/v0_2920bb57.py'; SRC_SHA = '2920bb5746c41cacacab2d11c84fe99d3f69ad784e3fa3743f8795ccc1fdfa3f'
V0B = ROOT / 'build/hinata/v0/fit-lq'; PHI = ROOT / 'build/hinata/v0/fit-lq-phi'
SPLITS = ROOT / 'build/learn/splits/games_split_v2.parquet'; HELDOUT = ROOT / 'docs/learning/splits/heldout-maps.json'
SPEC_PATH = ROOT / 'docs/learning/proposals/P-2-gate-spec.D-052.json'
SPEC_SHA = '15d79683518cf704a8cb7680ef1fa55acd8bdaef2bc97b694f40db742ea0d07d'
CPS = (10, 25, 50, 100, 150, 250, 400); B, SEED = 1000, 7
CELLS = [('post-m2', 'elim', c) for c in CPS] + [('post-m2', 'rl', c) for c in CPS]
POPS = {'ranked_clean': lambda x: x.ranked & x.clean, 'ranked': lambda x: x.ranked,
        'unranked_clean': lambda x: ~x.ranked & x.clean, 'unranked': lambda x: ~x.ranked, 'all': lambda x: x.ranked | ~x.ranked}
SPEC_KEYS = ('record', 'status', 'binding_population', 'reported_populations', 'min_coverage_per_map', 'bootstrap',
             'report_only_cells', 'min_cell_games', 'min_lb_all', 'late_rl_rounds', 'min_lb_late', 'slope_from_round',
             'slope_tol', 'rl50_min_auc', 'rl50_min_auc_binding', 'rl50_population')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fin(*v):
    return all(isinstance(x, (int, float, np.floating, np.integer)) and not isinstance(x, bool) and math.isfinite(float(x)) for x in v)


def load_spec(path=SPEC_PATH, frozen=True):
    """Only the exact D-052 file unlocks a claim."""
    path = Path(path); s = json.loads(path.read_text())
    miss = [k for k in SPEC_KEYS if k not in s]
    if miss:
        raise SystemExit(f'gate spec lacks {miss}')
    if frozen:
        h = sha(path)
        if h != SPEC_SHA or s['record'] != 'D-052' or not str(s['status']).startswith('FROZEN'):
            raise SystemExit(f'spec {path.name} sha {h[:12]} record {s["record"]} is not the frozen D-052 spec')
    if set(s['reported_populations']) - set(POPS) or s['binding_population'] not in POPS:
        raise SystemExit('spec population not implemented')
    return s


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
    pv = sig((xq[m.LQ].to_numpy(float) - 0.5) @ np.array([wv[k] for k in m.LQ], float))
    pp = sig((x[m.PHI].to_numpy(float) - 0.5) @ np.array([wp[k] for k in m.PHI], float))
    return pv, pp


# ---------- weighted metrics, vectorised over bootstrap replicates ----------
def wauc(y, p, W):
    """AUC with replicate weights W (R x n); ties count 1/2. NaN where a replicate has one class."""
    o = np.argsort(p, kind='mergesort'); y, p, W = y[o], p[o], W[:, o]
    _, start = np.unique(p, return_index=True); grp = np.repeat(np.arange(len(start)), np.diff(np.append(start, len(p))))
    Wn, Wp = W * (y == 0), W * (y == 1)
    gn = np.zeros((W.shape[0], len(start))); np.add.at(gn.T, grp, Wn.T)
    below = np.cumsum(gn, 1) - gn
    num = (Wp * (below[:, grp] + 0.5 * gn[:, grp])).sum(1); den = Wp.sum(1) * Wn.sum(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where(den > 0, num / den, np.nan)


def wslope(y, p, W, it=30):
    """Weighted logistic recalibration y ~ a + b·logit(p) by vectorised IRLS; (a, b) per replicate, NaN if singular."""
    p = np.clip(p, 1e-4, 1 - 1e-4); z = np.log(p / (1 - p)); R = W.shape[0]; ab = np.zeros((R, 2)); ab[:, 1] = 1
    ok = np.ones(R, bool)
    with np.errstate(all='ignore'):
        for _ in range(it):
            eta = ab[:, :1] + ab[:, 1:] * z; mu = 1 / (1 + np.exp(-eta)); v = W * mu * (1 - mu) + 1e-12; r = W * (y - mu)
            g = np.stack([r.sum(1), (r * z).sum(1)], 1)
            H = np.stack([np.stack([v.sum(1), (v * z).sum(1)], 1), np.stack([(v * z).sum(1), (v * z * z).sum(1)], 1)], 1)
            det = H[:, 0, 0] * H[:, 1, 1] - H[:, 0, 1] * H[:, 1, 0]; ok &= np.isfinite(det) & (np.abs(det) > 1e-12)
            Hs = np.where(ok[:, None, None], H, np.eye(2)); gs = np.where(ok[:, None], g, 0)
            ab = ab + np.linalg.solve(Hs, gs[..., None])[..., 0]
    ab[~ok] = np.nan
    return ab


def wbrier(y, p, W):
    return (W * (p - y) ** 2).sum(1) / W.sum(1)


def pct(a):
    a = a[np.isfinite(a)]
    return [float(np.percentile(a, 5)), float(np.percentile(a, 95))] if len(a) else [None, None]


def evaluate(pred, spec):
    """pred: one row per (game, cell) with y, p_v, p_phi, map, series_key, ranked, clean. Deterministic."""
    sk, inv = np.unique(pred.series_key.astype(str), return_inverse=True); pred = pred.assign(_s=inv)
    rng = np.random.default_rng(SEED); C = np.stack([np.bincount(rng.integers(0, len(sk), len(sk)), minlength=len(sk)) for _ in range(B)])
    out = []
    for pop in spec['reported_populations']:
        f = POPS[pop]
        for era, reg, cp in CELLS:
            x = pred[(pred.map_era == era) & (pred.regime == reg) & (pred['round'] == cp) & f(pred)]
            r = dict(population=pop, map_era=era, regime=reg, round=cp, n=len(x), pos=int(np.nansum(x.y)), neg=int(len(x) - np.nansum(x.y)),
                     series=int(x._s.nunique()), maps=sorted(x['map'].unique()))
            vals = x[['y', 'p_v', 'p_phi']].to_numpy(float)
            if len(x) and not np.isfinite(vals).all():
                r['status'] = 'NONFINITE_INPUT'; out.append(r); continue
            if not set(np.unique(x.y)) <= {0, 1}:
                r['status'] = 'BAD_LABEL'; out.append(r); continue
            if r['pos'] == 0 or r['neg'] == 0:
                r['status'] = 'UNDEFINED'; out.append(r); continue
            y = x.y.to_numpy(float); W1 = np.ones((1, len(x))); Wb = C[:, x._s.to_numpy()].astype(float); draws = {}
            for k, col in (('v', 'p_v'), ('phi', 'p_phi')):
                p = x[col].to_numpy(float)
                r[f'auc_{k}'] = float(wauc(y, p, W1)[0]); ab = wslope(y, p, W1)[0]; r[f'int_{k}'], r[f'slope_{k}'] = float(ab[0]), float(ab[1])
                r[f'brier_{k}'] = float(wbrier(y, p, W1)[0]); draws[f'a_{k}'] = wauc(y, p, Wb); abb = wslope(y, p, Wb)
                draws[f's_{k}'] = abb[:, 1]; r[f'slope_{k}_ci'], r[f'int_{k}_ci'] = pct(abb[:, 1]), pct(abb[:, 0])
            dd = draws['a_v'] - draws['a_phi']
            r['d_auc'] = r['auc_v'] - r['auc_phi']; r['d_auc_ci'] = pct(dd)
            r['valid_draws'] = int(min(np.isfinite(dd).sum(), np.isfinite(draws['s_v']).sum(), np.isfinite(draws['s_phi']).sum()))
            r['per_map'] = {m: dict(n=int(len(g)), auc_v=float(wauc(g.y.to_numpy(float), g.p_v.to_numpy(float), np.ones((1, len(g))))[0]),
                                    auc_phi=float(wauc(g.y.to_numpy(float), g.p_phi.to_numpy(float), np.ones((1, len(g))))[0]))
                            for m, g in x.groupby('map') if 0 < g.y.sum() < len(g)}
            r['status'] = 'OK'; out.append(r)
    return out


def gate(rows, spec, report_only):
    """Fail closed: a binding cell that is absent, one-class, non-finite or short of valid draws -> INCOMPLETE."""
    why, inc, rep = [], [], []
    T = {(r['population'], r['regime'], r['round']): r for r in rows}
    bp = spec['binding_population']; ro = set(report_only); mvd = spec['bootstrap']['min_valid_draws']
    for era, reg, cp in CELLS:
        if f'{reg}/r{cp}' in ro:
            continue
        r = T.get((bp, reg, cp))
        if r is None or r.get('status') != 'OK':
            inc.append(f'{bp}/{reg}/r{cp}: {"absent" if r is None else r.get("status")}'); continue
        lb = r['d_auc_ci'][0]
        if not fin(r['auc_v'], r['auc_phi'], r['d_auc'], lb, r['d_auc_ci'][1], r['slope_v'], r['slope_phi']):
            inc.append(f'{bp}/{reg}/r{cp}: non-finite metric'); continue
        if not r['valid_draws'] >= mvd:
            inc.append(f'{bp}/{reg}/r{cp}: {r["valid_draws"]} valid draws < {mvd}'); continue
        if not lb > spec['min_lb_all']:
            why.append(f'{reg}/r{cp}: ΔAUC 5th pct {lb:.4f} ≤ {spec["min_lb_all"]}')
        if reg == 'rl' and cp in spec['late_rl_rounds'] and not lb > spec['min_lb_late']:
            why.append(f'rl/r{cp}: ΔAUC 5th pct {lb:.4f} ≤ {spec["min_lb_late"]}')
        if cp >= spec['slope_from_round'] and not abs(r['slope_v'] - 1) <= abs(r['slope_phi'] - 1) + spec['slope_tol']:
            why.append(f'{reg}/r{cp}: |slope_V−1| {abs(r["slope_v"] - 1):.3f} > |slope_Φ−1| {abs(r["slope_phi"] - 1):.3f} + {spec["slope_tol"]}')
    r = T.get((spec['rl50_population'], 'rl', 50))
    if r is None or r.get('status') != 'OK' or not fin(r.get('auc_v'), r.get('auc_phi')):
        inc.append(f'{spec["rl50_population"]}/rl/r50: absent or non-finite')
    else:
        if not r['auc_v'] >= r['auc_phi']:
            why.append(f'rl/r50 AUC_V {r["auc_v"]:.4f} < AUC_Φ {r["auc_phi"]:.4f}')
        floor = r['auc_v'] >= spec['rl50_min_auc']
        rep.append(f'rl/r50 AUC_V {r["auc_v"]:.4f} vs {spec["rl50_min_auc"]}: {"met" if floor else "not met"} '
                   f'({"binding" if spec["rl50_min_auc_binding"] else "report-only"})')
        if spec['rl50_min_auc_binding'] and not floor:
            why.append(f'rl/r50 AUC_V {r["auc_v"]:.4f} < {spec["rl50_min_auc"]}')
    verdict = 'INCOMPLETE' if inc else ('PASS' if not why else 'FAIL')
    return dict(verdict=verdict, incomplete=inc, reasons=why, reported=rep, report_only_cells=sorted(ro))


def receipt(path, **kw):
    j = json.loads(path.read_text()) if path.exists() else {}
    j.setdefault('stages', []).append(dict(at=time.strftime('%FT%TZ', time.gmtime()), **kw)); path.write_text(json.dumps(j, indent=1, default=str))


def load_pop(path):
    pop = pd.read_parquet(path); meta = json.loads(Path(str(path) + '.json').read_text())
    assert sha(path) == meta['sha256'], 'population file changed'
    return pop, meta


def cmd_manifest(a):
    """Outcome-free: v2 split columns, decode presence (series parts, game ids only), store in_scope flag."""
    import duckdb
    hm = json.loads(HELDOUT.read_text())['heldout_maps']; assert sorted(hm) == ['Autarky', 'Maze', 'Trauma']
    q = ','.join(f"'{m}'" for m in hm)
    g = duckdb.sql(f"""select game, series_key, map, ranked, consumed_by from read_parquet('{SPLITS}')
                       where split = 'heldout_map' and map_era = 'post-m2' and in_scope and map in ({q})""").df()
    dec = duckdb.sql(f"select distinct game from read_parquet('{S1}/series/part-*.parquet', union_by_name=true)"
                     f" where game in (select game from g)").df()
    st = duckdb.sql(f"select game, in_scope from read_parquet('{S1}/games.parquet') where game in (select game from g)").df()
    sc = g.groupby('series_key').consumed_by.apply(lambda s: (s != '').any()); g['clean'] = ~g.series_key.map(sc)
    g['decoded'] = g.game.isin(dec.game); g['store_in_scope'] = g.game.isin(st.game[st.in_scope.fillna(False).astype(bool)])
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    g = g.drop(columns='consumed_by').sort_values('game').reset_index(drop=True); g.to_parquet(out)
    meta = dict(file=str(out), sha256=sha(out), splits_v2_sha=sha(SPLITS), heldout_sha=sha(HELDOUT), written=time.strftime('%FT%TZ', time.gmtime()),
                counts=g.groupby(['map', 'ranked', 'clean', 'decoded', 'store_in_scope']).size().rename('games').reset_index().to_dict('records'),
                note='No outcome column read (games_split_v2 has none; series parts read for game ids; games.parquet for in_scope only).')
    Path(str(out) + '.json').write_text(json.dumps(meta, indent=1, default=str)); print(json.dumps(meta, indent=1, default=str))


def coverage(pop, spec):
    b = pop[POPS[spec['binding_population']](pop)]; ok = b.decoded & b.store_in_scope
    cov = {m: dict(games=int(len(x)), usable=int(ok[x.index].sum()), coverage=float(ok[x.index].mean())) for m, x in b.groupby('map')}
    miss = [dict(game=str(r.game), map=r.map, reason='not decoded' if not r.decoded else 'in scope in manifest v2, out of scope in store games.parquet')
            for r in b[~ok].itertuples()]
    return cov, miss


def cmd_counts(a):
    """Per-cell game counts WITHOUT any outcome: side-A checkpoint rows of games still running (ended flag only, which is
    not the winner). Draws are not removed (that needs result_a), so counts are upper bounds on decisive rows."""
    import duckdb
    spec = load_spec(); pop, meta = load_pop(a.population); m = v0mod()
    g = pop[pop.decoded & pop.store_in_scope][['game', 'map', 'ranked', 'clean']]
    s = duckdb.sql(f"""select distinct game, round from read_parquet('{S1}/series/part-*.parquet', union_by_name=true)
                       where side = 'A' and round in ({','.join(map(str, CPS))}) and coalesce(ended, 0) = 0
                       and game in (select game from g)""").df()
    s = s.merge(g, on='game'); s['regime'] = [m.regime('post-m2', x) for x in s['map']]; s['round'] = s['round'].astype(int)
    tab = {pop_: {f'{reg}/r{cp}': int(((s.regime == reg) & (s['round'] == cp) & POPS[pop_](s)).sum()) for _, reg, cp in CELLS}
           for pop_ in spec['reported_populations']}
    bp = tab[spec['binding_population']]
    small = sorted(k for k, n in bp.items() if n < spec['min_cell_games'])
    ro = sorted(set(spec['report_only_cells']) | set(small), key=lambda k: (k.split('/')[0], int(k.split('/r')[1])))
    cov, miss = coverage(pop, spec)
    out = dict(written=time.strftime('%FT%TZ', time.gmtime()), spec_sha=SPEC_SHA, population_sha=meta['sha256'], scorer_sha=sha(SELF),
               counts=tab, report_only_cells=ro, report_only_by_count=small, coverage=cov, missing=miss,
               note='outcome-free: no result_a, no y read; ended flag and decode presence only; draws not removed')
    f = P2 / 'cell-counts.json'; f.write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1)); print('sha256', sha(f))


DEFAULT_SPEC = dict(record='SELFTEST', status='synthetic', binding_population='all', reported_populations=['all'], min_coverage_per_map=0.95,
                    bootstrap=dict(min_valid_draws=990), report_only_cells=[], min_cell_games=50, min_lb_all=-0.01,
                    late_rl_rounds=[150, 250, 400], min_lb_late=0.0, slope_from_round=25, slope_tol=0.05, rl50_min_auc=0.66,
                    rl50_min_auc_binding=False, rl50_population='all')


def cmd_selftest(a):
    """Development OOF from fit-lq stands in for predictions: plumbing and bootstrap only, never a confirmation."""
    oof = pd.read_parquet(V0B / 'oof.parquet'); tr = pd.read_parquet(V0B / 'train_rows.parquet')[['game', 'series_id', 'ranked']].drop_duplicates('game')
    x = oof.merge(tr, on='game', validate='many_to_one').rename(columns={'p_v0': 'p_v', 'series_id': 'series_key'})
    x['round'] = x['round'].astype(int); x['clean'] = True; x['ranked'] = x['ranked'].astype(bool)
    t0 = time.time(); rows = evaluate(x, DEFAULT_SPEC); g = gate(rows, DEFAULT_SPEC, [])
    keep = [r for r in rows if r['status'] == 'OK']
    print(pd.DataFrame([{k: r[k] for k in ('regime', 'round', 'n', 'series', 'auc_v', 'auc_phi', 'd_auc', 'd_auc_ci', 'slope_v', 'slope_phi', 'valid_draws')}
                        for r in keep]).round(5).to_string(index=False))
    print('SELFTEST gate (development OOF, NOT a confirmation):', g, f'{time.time() - t0:.0f}s')
    (P2 / 'selftest-r2.json').write_text(json.dumps(dict(rows=rows, gate=g, scorer_sha=sha(SELF)), indent=1, default=str))


def _claim(spec_sha, scorer_sha, report_only, cov, extra=None):
    P2.mkdir(parents=True, exist_ok=True); claim = P2 / 'CLAIM.json'
    fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)          # atomic one-shot: a second run fails here
    os.write(fd, json.dumps(dict(claimed=time.strftime('%FT%TZ', time.gmtime()), spec_sha=spec_sha, scorer_sha=scorer_sha,
                                 report_only_cells=report_only, coverage=cov, source_sha=SRC_SHA, B=B, seed=SEED, **(extra or {})),
                            indent=1, default=str).encode()); os.close(fd)
    receipt(P2 / 'RECEIPT.json', stage='claimed', claim_sha=sha(claim))
    return claim


def _seal(pred):
    pf = P2 / 'predictions.parquet'; pred.to_parquet(pf); os.chmod(pf, 0o444)
    receipt(P2 / 'RECEIPT.json', stage='sealed', predictions_sha=sha(pf), rows=len(pred), games=int(pred.game.nunique()))
    return pf


def cmd_run(a):
    spec = load_spec()                                                 # exact frozen D-052 file or refuse
    if a.audited_scorer_sha != sha(SELF):
        raise SystemExit(f'refused: scorer sha {sha(SELF)} differs from the audited {a.audited_scorer_sha}')
    pop, meta = load_pop(a.population); cc = json.loads((P2 / 'cell-counts.json').read_text())
    if (cc['spec_sha'], cc['population_sha'], cc['scorer_sha']) != (SPEC_SHA, meta['sha256'], sha(SELF)):
        raise SystemExit('refused: cell-counts.json was not produced from this spec, population and scorer; rerun counts')
    cov, miss = coverage(pop, spec)
    if any(v['coverage'] < spec['min_coverage_per_map'] for v in cov.values()):
        raise SystemExit(f'refused before claim: coverage {cov}')
    m = v0mod(); w, wh = weights()
    bad = [c for c, (wv, wp) in w.items() if wv is None or wp is None or not fin(*wv.values(), *wp.values())]
    _claim(SPEC_SHA, sha(SELF), cc['report_only_cells'], cov,
           dict(population_sha=meta['sha256'], counts_sha=sha(P2 / 'cell-counts.json'), weight_files=wh,
                missing_cells=[list(c) for c in bad], missing_games=miss))
    rc = P2 / 'RECEIPT.json'
    try:
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
        pred = pd.concat(parts, ignore_index=True); pf = _seal(pred)
        print('sealed', pf, sha(pf)); print('now: p2_confirm.py score')
    except BaseException as e:
        receipt(rc, stage='error', error=repr(e)); raise


def cmd_score(a, spec_path=SPEC_PATH, spec_sha=SPEC_SHA):
    cp_, rcp, pf = P2 / 'CLAIM.json', P2 / 'RECEIPT.json', P2 / 'predictions.parquet'
    rc = json.loads(rcp.read_text()); st = rc['stages']
    if any(s['stage'] == 'scored' for s in st):
        raise SystemExit('refused: already scored (one claim, one score)')
    claimed = [s for s in st if s['stage'] == 'claimed']; sealed = [s for s in st if s['stage'] == 'sealed']
    inc = []
    if not claimed or not sealed:
        inc.append('no claimed or no sealed stage in the receipt')
    elif sha(cp_) != claimed[0]['claim_sha']:
        inc.append('claim hash differs from the hash recorded at claim time')
    claim = json.loads(cp_.read_text())
    if sha(SELF) != claim.get('scorer_sha'):
        inc.append(f'scorer hash {sha(SELF)[:12]} differs from the audited/claimed {str(claim.get("scorer_sha"))[:12]}')
    if sha(spec_path) != spec_sha or claim.get('spec_sha') != spec_sha:
        inc.append('gate spec hash differs from the frozen one')
    if sealed and (not pf.exists() or sha(pf) != sealed[0]['predictions_sha']):
        inc.append('predictions changed after sealing')
    if claim.get('missing_cells'):
        inc.append(f'model file missing or non-finite: {claim["missing_cells"]}')
    rows = []
    if not inc:
        spec = json.loads(Path(spec_path).read_text())
        if any(v['coverage'] < spec['min_coverage_per_map'] for v in claim['coverage'].values()):
            inc.append('coverage below min_coverage_per_map')
    if inc:
        g = dict(verdict='INCOMPLETE', incomplete=inc, reasons=[], reported=[])
    else:
        rows = evaluate(pd.read_parquet(pf), spec); g = gate(rows, spec, claim['report_only_cells'])
    res = P2 / 'result.json'; res.write_text(json.dumps(dict(gate=g, rows=rows), indent=1, default=str))
    receipt(rcp, stage='scored', verdict=g['verdict'], result_sha=sha(res), scorer_sha=sha(SELF)); print(json.dumps(g, indent=1))
    return g


def _synth(n=1500, seed=0):
    r = np.random.default_rng(seed); g = np.arange(n); s = r.normal(0, 1.2, n); y = (r.random(n) < 1 / (1 + np.exp(-s))).astype(float)
    mp = r.choice(['Autarky', 'Maze', 'Trauma'], n); rk = r.random(n) < .7; cl = r.random(n) < .7; rows = []
    for cp in CPS:
        sv = s + r.normal(0, 0.2, n); sp = 0.6 * s + r.normal(0, 0.8, n)
        rows.append(pd.DataFrame(dict(game=g.astype(str), series_key=(g // 5).astype(str), map=mp, map_era='post-m2',
                                      regime=np.where(mp == 'Autarky', 'elim', 'rl'), round=cp, ranked=rk, clean=cl, y=y,
                                      p_v=1 / (1 + np.exp(-sv)), p_phi=1 / (1 + np.exp(-sp)))))
    return pd.concat(rows, ignore_index=True)


def cmd_probe(a):
    """Tanaka's malformed-input and integrity probes on synthetic data, each in its own scratch claim dir."""
    global P2
    real = P2; sp = Path(tempfile.mkdtemp()) / 'spec.json'
    spec = dict(DEFAULT_SPEC, binding_population='ranked_clean', reported_populations=['ranked_clean', 'all'], rl50_population='ranked_clean')
    sp.write_text(json.dumps(spec)); ssha = sha(sp); cov = {'Autarky': dict(coverage=1.0)}; res = []

    def case(name, expect, mutate_pred=None, mutate_claim=None, claim_scorer=None, gate_only=None):
        global P2
        P2 = Path(tempfile.mkdtemp())
        if gate_only is not None:
            got = gate(gate_only, spec, [])['verdict']
        else:
            pred = _synth()
            if mutate_pred:
                pred = mutate_pred(pred)
            c = _claim(ssha, claim_scorer or sha(SELF), [], cov); _seal(pred)
            if mutate_claim:
                j = json.loads(c.read_text()); mutate_claim(j); c.write_text(json.dumps(j))
            try:
                got = cmd_score(a, spec_path=sp, spec_sha=ssha)['verdict']
            except SystemExit as e:
                got = f'refused: {e}'
        res.append(dict(case=name, expect=expect, got=got, ok=got.startswith(expect))); print(res[-1])

    case('valid synthetic control', 'PASS')
    good = evaluate(_synth(), spec)
    for fld in ('slope_v', 'slope_phi', 'auc_v', 'auc_phi'):
        bad = [dict(r) for r in good]
        for r in bad:
            if r['regime'] == 'rl' and r['round'] == 50:
                r[fld] = float('nan')
        case(f'rl/r50 {fld}=NaN (gate)', 'INCOMPLETE', gate_only=bad)
    bad = [dict(r) for r in good]
    for r in bad:
        if r['regime'] == 'rl' and r['round'] == 50:
            r['d_auc_ci'] = [float('nan'), float('nan')]
    case('rl/r50 ΔAUC interval NaN (gate)', 'INCOMPLETE', gate_only=bad)
    case('NaN prediction in a binding cell', 'INCOMPLETE',
         mutate_pred=lambda p: p.assign(p_v=np.where((p.regime == 'rl') & (p['round'] == 100) & (p.index % 7 == 0), np.nan, p.p_v)))
    case('one-class binding cell', 'INCOMPLETE', mutate_pred=lambda p: p.assign(y=np.where((p.regime == 'elim') & (p['round'] == 25), 1.0, p.y)))

    def few(p):
        m = (p.regime == 'elim') & (p['round'] == 150) & p.ranked & p.clean; p = p.copy(); p.loc[m, 'y'] = 0.0
        first = p.loc[m].series_key.iloc[0]; p.loc[m & (p.series_key == first), 'y'] = 1.0; return p
    case('valid draws < 990 (positives in one series)', 'INCOMPLETE', mutate_pred=few)
    case('claim report-only list changed after claim', 'INCOMPLETE', mutate_claim=lambda j: j.__setitem__('report_only_cells', ['rl/r50']))
    case('claim scorer hash differs', 'INCOMPLETE', claim_scorer='0' * 64)
    P2 = Path(tempfile.mkdtemp()); _claim(ssha, sha(SELF), [], cov); _seal(_synth()); cmd_score(a, spec_path=sp, spec_sha=ssha)
    try:
        cmd_score(a, spec_path=sp, spec_sha=ssha); got = 'scored twice'
    except SystemExit as e:
        got = f'refused: {e}'
    res.append(dict(case='second score', expect='refused', got=got, ok=got.startswith('refused'))); print(res[-1])
    for name, path in (('PROPOSED spec', ROOT / 'docs/learning/proposals/P-hinata-02-gate-spec.PROPOSED.json'), ('synthetic spec', sp)):
        try:
            load_spec(path); got = 'accepted'
        except SystemExit as e:
            got = f'refused: {e}'
        res.append(dict(case=f'{name} as frozen', expect='refused', got=got, ok=got.startswith('refused'))); print(res[-1])
    try:
        load_spec(); got = 'accepted'
    except SystemExit as e:
        got = f'refused: {e}'
    res.append(dict(case='D-052 frozen spec', expect='accepted', got=got, ok=got == 'accepted')); print(res[-1])
    P2 = real; out = dict(scorer_sha=sha(SELF), written=time.strftime('%FT%TZ', time.gmtime()), passed=sum(r['ok'] for r in res), of=len(res), cases=res)
    (P2 / 'probe-r2.json').write_text(json.dumps(out, indent=1, default=str)); print(f"PROBES {out['passed']}/{out['of']}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['manifest', 'counts', 'selftest', 'probe', 'run', 'score'])
    ap.add_argument('--out', default='build/hinata/p2/population.parquet')
    ap.add_argument('--population', default='build/hinata/p2/population.parquet')
    ap.add_argument('--audited-scorer-sha')
    a = ap.parse_args(); dict(manifest=cmd_manifest, counts=cmd_counts, selftest=cmd_selftest, probe=cmd_probe, run=cmd_run, score=cmd_score)[a.cmd](a)
