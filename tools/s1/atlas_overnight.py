"""Overnight strategy-atlas run (S1). One command, resumable, time-boxed. Run from anywhere on the Mac:

  .venv/bin/python tools/s1/atlas_overnight.py check            # 1 game + decode: proves the toolchain (≈30 s)
  .venv/bin/python tools/s1/atlas_overnight.py all --hours 11.5  # the night: decode -> select -> run -> decode

Stages (each resumable; `all` runs them in order and stops submitting games in time to decode them):
  decode   decode a stratified sample of the ~35k existing local replays on the ladder maps (experiment_data/*) into the
           s1 local store: up to 3 games per bot per map, bots seen on >= 8 maps. Zero new games.
  select   local strength (Bradley-Terry on the 133k existing local results), behaviour vectors per bot (field z-scores,
           per map, pooled), k-means niches, novelty; writes the priority plan build/atlas/plan.json:
             P0 anchors (bots that were live as team 7), the FRONTIER list, bots newer than the results (latest per family)
             P1 niche elites: the 3 strongest bots of each niche
             P2 novel bots (far from their neighbours) with at least median strength
             P3 everyone else with a vector, strongest first
  run      a fixed panel on the 10 ladder maps, both seats, seed 1: pass A vs 3 opponents, pass B vs 3 more, in the tier
           order P0A, P1A, P0B, P2A, P1B, P3A, P2B, P3B until the deadline. Replays: build/atlas/panel/replays/.
  decodepanel  decode the panel replays into the local store (run 'atlas-panel').
Everything is logged to build/atlas/overnight.log. Nothing outside build/ is written.
"""
import argparse, json, os, random, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
if sys.platform.startswith('linux') and (ROOT / 'build' / 's1-pylib').exists():
    sys.path.append(str(ROOT / 'build' / 's1-pylib'))
os.environ.setdefault('S1_FREEZE', '1')          # never rebuild the field norms mid-run
import numpy as np
import pandas as pd

ATLAS = ROOT / 'build' / 'atlas'
PANEL_DIR = ATLAS / 'panel'
LOG = ATLAS / 'overnight.log'
LIVE_MAPS = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma', 'autarky',
             'devil', 'trauma']
PANEL_A = ['fenrir-v20-crowded-resource-revalue', 'gavroche-v66-supported-safe', 'hunter-v20-portal-scouts']
PANEL_B = ['tyr-v12-devil-scout-tiebreak', 'sinbad-v07-divecap', 'kraken-v04-eval']
ANCHORS = ['tyr-v12-devil-scout-tiebreak', 'ares-v35-crown-clipped-dash-threat', 'ares-v36-no-pearl-portal-scout',
           'ares-v37-near-portal-scout', 'ares-v06-expanded-search-support', 'yuna-v05-core', 'chaewon-y04-probe']
RESULTS_CUTOFF = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)   # the existing local results end here
FEATS_150 = ['pearls_per_dt', 'bed_pearls_per_dt', 'corpse_pearl_share', 'births_per_dt', 'own_goals_per1k',
             'transits_per_dt', 'rays_per_dt', 'idle_share', 'turnaround_share', 'disp_per_turn', 'clustered_share',
             'nn_dist_mean', 'swarm_rg', 'enemy_head_dist_mean', 'contact_share', 'top1_share', 'mean_len',
             'kelp_adj_mean', 'reach_le8_share', 'steps_per_pearl', 'transit_died3_share']
FEATS_50 = ['pearls_per_dt', 'births_per_dt', 'disp_per_turn', 'transits_per_dt', 'clustered_share']
FEATS_SIDES = ['death_suicide_per1k', 'death_invalid_per1k', 'child_len_le3_share', 'sprint_share', 'first_split',
               'first_pearl', 'rays_toward_enemy_share', 'ray_refracted_share', 'seen50']


def log(*a):
    ATLAS.mkdir(parents=True, exist_ok=True)
    msg = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + ' '.join(str(x) for x in a)
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')


def unswbc_exe():
    for c in (os.environ.get('UNSWBC'), str(ROOT / '.venv' / 'bin' / 'unswbc'), str(Path(sys.executable).parent / 'unswbc')):
        if c and Path(c).is_file():
            return c
    import shutil
    c = shutil.which('unswbc')
    if c:
        return c
    raise SystemExit('unswbc not found: uv pip install --python .venv/bin/python unswbc==1.2.2')


# ------------------------------------------------------------------ stage: decode existing local replays
def stage_decode(jobs, budget_s, per=3, min_maps=8):
    from tools.s1 import build as B
    R = pd.read_parquet(ATLAS / 'local_replays.parquet')
    R = R[R['map'].isin(LIVE_MAPS)].copy()
    long = pd.concat([R.assign(bot=R.a), R.assign(bot=R.b)])
    maps_per_bot = long.groupby('bot')['map'].nunique()
    keep_bots = set(maps_per_bot[maps_per_bot >= min_maps].index)
    long = long[long.bot.isin(keep_bots)].sample(frac=1, random_state=7)
    pick = set(long.groupby(['bot', 'map']).head(per).path)
    store = B.OUT / 'local'
    store.mkdir(parents=True, exist_ok=True)
    done = B.done_games(store)
    tasks = [(p, f'atlas-existing/{Path(p).stem}', dict(source='local', run='atlas-existing')) for p in sorted(pick)
             if f'atlas-existing/{Path(p).stem}' not in done]
    log(f'decode: {len(keep_bots)} bots, {len(pick)} replays picked, {len(tasks)} to decode with {jobs} jobs')
    if tasks:
        B.run_batch(store, tasks, jobs, budget_s)
    log('decode: done')


# ------------------------------------------------------------------ stage: select
def bt_strength(res):
    """ridge Bradley-Terry with a seat term over every existing local result; Elo scale, centred at 1500"""
    from scipy.optimize import minimize
    r = res[res.outcome.isin(['A', 'B'])]
    bots = pd.Index(sorted(set(r.bot_a) | set(r.bot_b)))
    a, b = bots.get_indexer(r.bot_a), bots.get_indexer(r.bot_b)
    y = (r.outcome == 'A').values.astype(float)
    n = len(bots)

    def f(x):
        s, c = x[:n], x[n]
        z = s[a] - s[b] + c
        p = 1 / (1 + np.exp(-z))
        e = p - y
        g = np.bincount(a, e, minlength=n) - np.bincount(b, e, minlength=n) + 0.5 * s
        return np.sum(np.logaddexp(0, z) - y * z) + 0.25 * np.sum(s * s), np.concatenate([g, [e.sum()]])
    x = minimize(f, np.zeros(n + 1), jac=True, method='L-BFGS-B').x
    games = pd.concat([r.bot_a, r.bot_b]).value_counts()
    return pd.DataFrame(dict(bot=bots, bt_elo=1500 + x[:n] * 400 / np.log(10), bt_games=games.reindex(bots).values))


def vectors(con):
    have = set(con.execute('describe l_series_z').df().column_name)
    f150 = [c for c in FEATS_150 if c in have]
    f50 = [c for c in FEATS_50 if c in have]
    q = lambda cols, r: ', '.join(f'avg("{c}") as "{c}{"" if r == 150 else "_r50"}"' for c in cols)
    a = con.execute(f"select name as bot, map, count(*) as n, {q(f150, 150)} from l_series_z where round = 150 group by 1, 2").df()
    b = con.execute(f"select name as bot, map, {q(f50, 50)} from l_series_z where round = 50 group by 1, 2").df()
    hs = set(con.execute('describe l_sides_z').df().column_name)
    fs = [c for c in FEATS_SIDES if c in hs]
    agg = ', '.join('avg("%s") as "%s"' % (x, x) for x in fs)
    c = con.execute(f"select name as bot, map, {agg} from l_sides_z group by 1, 2").df()
    return a.merge(b, on=['bot', 'map'], how='left').merge(c, on=['bot', 'map'], how='left')


def kmeans(X, k, seed=0, iters=100, restarts=10):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(iters):
            d = ((X[:, None, :] - C[None]) ** 2).sum(-1)
            lab = d.argmin(1)
            C2 = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(C2, C):
                break
            C = C2
        inertia = ((X - C[lab]) ** 2).sum()
        if best is None or inertia < best[0]:
            best = (inertia, lab, C)
    return best[1], best[2]


def family_version(name):
    m = re.match(r'^(.*?)-([a-z])(\d+)(?:-|$)', name)
    return (m.group(1), int(m.group(3))) if m else (name, 0)


def bot_mtime(d):
    ts = [p.stat().st_mtime for p in Path(d).rglob('*') if p.is_file() and '.unswbc-build' not in p.parts]
    return max(ts) if ts else 0


def stage_select(k=12):
    from tools.s1.q import connect
    res = pd.read_parquet(ATLAS / 'local_results.parquet')
    S = bt_strength(res)
    con = connect('local', norms=True)
    V = vectors(con)
    V.to_parquet(ATLAS / 'vectors_existing.parquet', index=False)
    feats = [c for c in V.columns if c not in ('bot', 'map', 'n')]
    # pooled vector: each map counts equally; shrink toward the field (0) by games
    per_bot = V.groupby('bot').apply(lambda d: pd.Series({**{f: np.nanmean(d[f]) for f in feats}, 'n': d.n.sum(), 'maps': len(d)}))
    per_bot = per_bot[per_bot.n >= 10]
    Xr = per_bot[feats].fillna(0).values * (per_bot.n.values / (per_bot.n.values + 5))[:, None]
    mu, sd = Xr.mean(0), Xr.std(0) + 1e-9
    X = np.clip((Xr - mu) / sd, -4, 4)
    lab, C = kmeans(X, min(k, max(2, len(X) // 8)))
    d = np.sqrt(((X[:, None, :] - X[None]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    novelty = np.sort(d, 1)[:, :5].mean(1)
    P = per_bot.reset_index()[['bot', 'n', 'maps']].assign(niche=lab, novelty=novelty).merge(S, on='bot', how='left')
    # inventory of runnable bots
    inv = []
    for t in sorted((ROOT / 'bots').glob('*/bot.toml')):
        name = t.parent.name
        fam, ver = family_version(name)
        inv.append(dict(bot=name, family=fam, version=ver, mtime=bot_mtime(t.parent)))
    I = pd.DataFrame(inv)
    runnable = set(I.bot)
    known = set(S.bot)
    newer = I[(~I.bot.isin(known)) & (I.mtime >= RESULTS_CUTOFF.timestamp())]
    newer = newer.sort_values('version').groupby('family').tail(1).sort_values('mtime', ascending=False).head(40)
    front = re.findall(r'\|\s*[^|]*\|\s*`([A-Za-z0-9_\-]+)`', (ROOT / 'FRONTIER.md').read_text())
    plan, seen = [], set()

    def add(bots, tier, why):
        for b in bots:
            if b in runnable and b not in seen:
                seen.add(b)
                plan.append(dict(bot=b, tier=tier, why=why))
    add(ANCHORS, 'P0', 'anchor: live as team 7 / reference')
    add(front, 'P0', 'FRONTIER')
    add(newer.bot, 'P0', 'newer than the local results (latest in family)')
    elites = P[P.bt_games >= 30].sort_values('bt_elo', ascending=False).groupby('niche').head(3)
    add(elites.bot, 'P1', 'niche elite')
    # novelty only counts with strength: at least the 60th percentile of local strength, and ranked by novelty x strength
    floor = P.bt_elo.quantile(0.6)
    q = P[(P.bt_elo >= floor) & (P.bt_games >= 30)].copy()
    q['score'] = q.novelty.rank(pct=True) + q.bt_elo.rank(pct=True)
    add(q.sort_values('score', ascending=False).head(30).bot, 'P2', 'novel and strong (>= 60th pct strength)')
    add(P.sort_values('bt_elo', ascending=False).bot, 'P3', 'rest by strength')
    json.dump(dict(created=time.strftime('%Y-%m-%d %H:%M:%S'), panel_a=PANEL_A, panel_b=PANEL_B, plan=plan),
              open(ATLAS / 'plan.json', 'w'), indent=1)
    P.to_parquet(ATLAS / 'bots_existing.parquet', index=False)
    tiers = pd.Series([p['tier'] for p in plan]).value_counts().to_dict()
    log(f'select: {len(P)} bots with vectors, {len(S)} with strength, niches {len(set(lab))}; plan {len(plan)} bots {tiers}')


# ------------------------------------------------------------------ stage: run
def fixture_list(bot, opps):
    out = []
    for o in opps:
        if o == bot:
            continue
        for m in LIVE_MAPS:
            for a, b in ((bot, o), (o, bot)):
                out.append(dict(map=m, a=a, b=b, game=f's1__{m}__{a}__{b}'))
    return out


def compile_bot(name, built, failed):
    if name in built or name in failed:
        return name in built
    try:
        from unswbc.project import Project
        Project.from_dir(ROOT / 'bots' / name).compile()
        built.add(name)
        return True
    except ImportError:
        built.add(name)          # older toolkit without the API: the first game builds it
        return True
    except Exception as e:
        failed[name] = str(e)[:300]
        log(f'BUILD FAILED {name}: {failed[name]}')
        return False


def play(fx, exe):
    rep = PANEL_DIR / 'replays' / (fx['game'] + '.replay')
    if rep.exists():
        return None
    t = time.time()
    try:
        p = subprocess.run([exe, 'run', '--seed', '1', '--no-logs', '--no-indicator', '--no-draw', '-o', str(rep) + '.tmp',
                            f"maps/{fx['map']}.map", f"bots/{fx['a']}", f"bots/{fx['b']}"],
                           capture_output=True, text=True, timeout=900)
        out = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = 'timeout', -9
    m = re.search(r'team (A|B) wins after (\d+) rounds \(([^)]*)\)', out)
    if os.path.exists(str(rep) + '.tmp'):
        os.replace(str(rep) + '.tmp', rep)
    return dict(fx, seconds=round(time.time() - t, 1), rc=rc, winner=m.group(1) if m else ('draw' if 'draw' in out.lower() else None),
                rounds=int(m.group(2)) if m else None, reason=m.group(3) if m else out.strip()[-200:])


def stage_run(jobs, deadline):
    exe = unswbc_exe()
    plan = json.load(open(ATLAS / 'plan.json'))['plan']
    (PANEL_DIR / 'replays').mkdir(parents=True, exist_ok=True)
    built, failed = set(), {}
    opps_a = [o for o in PANEL_A if compile_bot(o, built, failed)]
    opps_b = [o for o in PANEL_B if compile_bot(o, built, failed)]
    by = {t: [p['bot'] for p in plan if p['tier'] == t] for t in ('P0', 'P1', 'P2', 'P3')}
    order = [('P0', 'A'), ('P1', 'A'), ('P0', 'B'), ('P2', 'A'), ('P1', 'B'), ('P3', 'A'), ('P2', 'B'), ('P3', 'B')]
    queue = []
    for tier, ps in order:
        for b in by[tier]:
            queue.append((b, opps_a if ps == 'A' else opps_b, f'{tier}{ps}'))
    idx = open(PANEL_DIR / 'index.jsonl', 'a')
    n_done, t0, running = 0, time.time(), set()
    log(f'run: {len(queue)} bot-passes queued, jobs {jobs}, deadline {time.strftime("%H:%M", time.localtime(deadline))}, unswbc {exe}')
    with ThreadPoolExecutor(jobs) as ex:
        futs = set()
        qi = 0
        pending_fx = []
        while True:
            # keep the pool fed
            while len(futs) < jobs * 2 and time.time() < deadline:
                if not pending_fx:
                    if qi >= len(queue):
                        break
                    b, opps, label = queue[qi]
                    qi += 1
                    if not compile_bot(b, built, failed):
                        continue
                    pending_fx = [f for f in fixture_list(b, opps)
                                  if not (PANEL_DIR / 'replays' / (f['game'] + '.replay')).exists()]
                    if pending_fx:
                        log(f'run: {label} {b} ({len(pending_fx)} games)')
                    continue
                futs.add(ex.submit(play, pending_fx.pop(), exe))
            if not futs:
                break
            done = next(as_completed(futs))
            futs.discard(done)
            try:
                row = done.result()
            except Exception as e:
                log('ERR', e)
                continue
            if row:
                idx.write(json.dumps(row) + '\n')
                idx.flush()
                n_done += 1
                if n_done % 100 == 0:
                    rate = n_done / (time.time() - t0) * 3600
                    log(f'run: {n_done} games, {rate:.0f}/h, queue position {qi}/{len(queue)}')
    json.dump(failed, open(ATLAS / 'build_failures.json', 'w'), indent=1)
    log(f'run: stopped with {n_done} games this session ({len(failed)} build failures)')


def stage_decode_panel(jobs, budget_s):
    from tools.s1 import build as B
    store = B.OUT / 'local'
    done = B.done_games(store)
    files = sorted((PANEL_DIR / 'replays').glob('*.replay'))
    tasks = [(str(p), f'atlas-panel/{p.stem}', dict(source='local', run='atlas-panel')) for p in files
             if f'atlas-panel/{p.stem}' not in done]
    log(f'decodepanel: {len(tasks)} replays to decode')
    if tasks:
        B.run_batch(store, tasks, jobs, budget_s)
    log('decodepanel: done')


def stage_check():
    exe = unswbc_exe()
    log(f'check: python {sys.version.split()[0]}, unswbc {subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.strip()}')
    import duckdb, scipy  # noqa: F401  (fail early if the analysis stack is missing)
    for need in (ATLAS / 'local_replays.parquet', ATLAS / 'local_results.parquet', ROOT / 'build' / 's1' / 'corpus' / 'norm_series.parquet'):
        if not need.exists():
            raise SystemExit(f'missing {need}')
    built, failed = set(), {}
    for o in PANEL_A + PANEL_B:
        compile_bot(o, built, failed)
    if failed:
        log(f'check: WARNING panel opponents that failed to build will be skipped: {list(failed)}')
    PANEL_DIR.joinpath('check').mkdir(parents=True, exist_ok=True)
    t = time.time()
    p = subprocess.run([exe, 'run', '--seed', '1', '--no-logs', '--no-indicator', '--no-draw', '-o', str(PANEL_DIR / 'check' / 'check.replay'),
                        'maps/default.map', f'bots/{PANEL_A[0]}', f'bots/{PANEL_A[2]}'], capture_output=True, text=True, timeout=600)
    if p.returncode != 0 or not (PANEL_DIR / 'check' / 'check.replay').exists():
        raise SystemExit('check game failed:\n' + (p.stdout + p.stderr)[-1500:])
    from tools.s1.build import process
    r = process((str(PANEL_DIR / 'check' / 'check.replay'), 'check', {}))
    if 'error' in r:
        raise SystemExit(f'check decode failed: {r["error"]}')
    log(f'check: OK - one game in {time.time() - t:.0f}s, decoded ({len(r["series"])} series rows). Ready for `all`.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage', choices=['check', 'decode', 'select', 'run', 'decodepanel', 'all'])
    ap.add_argument('--hours', type=float, default=11.5)
    ap.add_argument('--jobs', type=int, default=max(2, (os.cpu_count() or 4) - 2), help='parallel games')
    ap.add_argument('--decode-jobs', type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    start = time.time()
    end = start + a.hours * 3600
    if a.stage == 'check':
        return stage_check()
    log(f'=== {a.stage} start: {a.hours} h, {a.jobs} game jobs, {a.decode_jobs} decode jobs, cpus {os.cpu_count()}')
    if a.stage in ('decode', 'all'):
        stage_decode(a.decode_jobs, budget_s=2.5 * 3600)
    if a.stage in ('select', 'all'):
        stage_select()
    if a.stage in ('run', 'all'):
        # leave time to decode what was played: ~1 s per replay per decode core, plus margin
        reserve = 2400
        stage_run(a.jobs, end - reserve)
    if a.stage in ('decodepanel', 'all'):
        stage_decode_panel(a.decode_jobs, budget_s=max(600, end - time.time()))
    log(f'=== {a.stage} finished after {(time.time() - start) / 3600:.2f} h')


if __name__ == '__main__':
    main()
