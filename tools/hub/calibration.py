"""Live-versus-offline calibration (Part B §9.3), day-one form.

Every cycle on the Mac: map each live source to its repository bot directory (legacy fingerprint over top-level
.py/.toml files), read the shared local ledger (`game_stats.parquet`, PyArrow), compute the local win share of that
source on the ten live maps (all local opponents, native mode) and its live controlled field win share, and store an
`absolute` calibration row when either count changed. For a running experiment whose candidate and control both map
to local bots, store a `paired` row: local paired delta over common (map, opponent) cells versus the live paired
block delta. Then fit the expectation model live = a + b·local over sources with enough games; with fewer than five
such sources the model is "band mean" (expect the mean live share of our sources whatever the local number says).
"""
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

from . import db

LIVE_MAPS = {'schooltime': 'Schooltime', 'portals': 'Portals', 'slithery_fight': 'Slithery Fight', 'queen_of_spades': 'Queen Of Spades',
             'default': 'Default', 'trophy': 'Trophy', 'dilemma': 'Prisoners Dilemma', 'autarky': 'Autarky', 'devil': 'Devil', 'trauma': 'Trauma'}
REFERENCE_SET = {'yuna-v02-core', 'gavroche-v32-supported-divecap', 'sinbad-v07-divecap', 'hunter-v20-portal-scouts', 'kraken-v04-eval',
                 'ouroboros-v10-beacon', 'ouroboros-m01-vibing-mimic', 'witten-x03-confirmed-fastbed'}
MIN_LIVE, MIN_LOCAL, MIN_MODEL_LIVE, MIN_MODEL_LOCAL, MIN_MODEL_POINTS = 10, 10, 20, 30, 5


def legacy_fingerprint(directory):
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(directory).iterdir()) if p.is_file() and p.suffix in ('.py', '.toml')}
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest() if files else None


def bot_index(repo):
    """fingerprint -> bot directory name for every bot in the repository; falls back to build/bot_legacy_fingerprints.json
    (a snapshot written on the Mac) when the bots directory is not readable here."""
    out = {}
    bots = Path(repo) / 'bots'
    if bots.exists():
        for d in sorted(bots.iterdir()):
            if d.is_dir():
                try:
                    fp = legacy_fingerprint(d)
                except OSError:
                    continue
                if fp and fp not in out:
                    out[fp] = d.name
    snapshot = Path(repo) / 'build' / 'bot_legacy_fingerprints.json'
    if snapshot.exists():
        try:
            for fp, name in json.loads(snapshot.read_text()).items():
                out.setdefault(fp, name)
        except ValueError:
            pass
    if bots.exists():
        try:
            (Path(repo) / 'build').mkdir(exist_ok=True)
            snapshot.write_text(json.dumps({fp: n for fp, n in out.items()}, indent=0))
        except OSError:
            pass
    return out


def load_ledger(repo):
    """Rows of the shared local ledger restricted to live-pool maps; None if PyArrow or the file is unavailable."""
    try:
        import pyarrow.parquet as pq
    except ImportError:
        return None
    path = Path(repo) / 'game_stats.parquet'
    if not path.exists():
        return None
    table = pq.read_table(str(path), columns=['bot_a', 'bot_b', 'map', 'mode', 'runner_version', 'outcome', 'a_wins', 'b_wins', 'draws', 'runtime_faults'])
    rows = [r for r in table.to_pylist() if r['map'] in LIVE_MAPS]
    return rows


def local_profile(ledger, bot):
    rows = [r for r in ledger if (r['bot_a'] == bot or r['bot_b'] == bot) and r['mode'] == 'native']
    if not rows:
        return None
    scores, ref, by_map, by_opp = [], [], defaultdict(list), defaultdict(list)
    for r in rows:
        me = 'a' if r['bot_a'] == bot else 'b'
        opp = r['bot_b'] if me == 'a' else r['bot_a']
        s = (r[me + '_wins'] or 0) + 0.5 * (r['draws'] or 0)
        scores.append(s)
        by_map[LIVE_MAPS[r['map']]].append(s)
        by_opp[opp].append(s)
        if opp in REFERENCE_SET:
            ref.append(s)
    return dict(n=len(scores), share=round(sum(scores) / len(scores), 3), n_ref=len(ref), share_ref=round(sum(ref) / len(ref), 3) if ref else None,
                opponents=len(by_opp), by_map={m: round(sum(v) / len(v), 2) for m, v in by_map.items()},
                by_opponent={o: (len(v), round(sum(v) / len(v), 2)) for o, v in by_opp.items()},
                toolkits=sorted({r['runner_version'] for r in rows if r.get('runner_version')}))


def live_profile(conn, submission):
    rows = db.rows(conn, "SELECT score, map_name, opponent_team FROM games WHERE verified=1 AND origin='controlled' AND pool='field' AND own_submission=?", (submission,))
    if not rows:
        return None
    by_map = defaultdict(list)
    for r in rows:
        by_map[r['map_name']].append(r['score'] or 0)
    return dict(n=len(rows), share=round(sum(r['score'] or 0 for r in rows) / len(rows), 3), opponents=len({r['opponent_team'] for r in rows}),
                by_map={m: round(sum(v) / len(v), 2) for m, v in by_map.items()})


def source_map(conn, index):
    """submission id -> (fingerprint, bot directory) for every hub candidate with an upload and a matching bot."""
    out = {}
    for c in db.rows(conn, 'SELECT name, fingerprint, submission_id FROM candidates WHERE submission_id IS NOT NULL'):
        bot = index.get(c['fingerprint'])
        if bot:
            out[c['submission_id']] = (c['fingerprint'], bot, c['name'])
    return out


def last_row(conn, fingerprint, measure, control=None):
    if control:
        return conn.execute('SELECT * FROM calibration WHERE fingerprint=? AND measure=? AND control_fingerprint=? ORDER BY id DESC LIMIT 1', (fingerprint, measure, control)).fetchone()
    return conn.execute('SELECT * FROM calibration WHERE fingerprint=? AND measure=? ORDER BY id DESC LIMIT 1', (fingerprint, measure)).fetchone()


def paired_local(ledger, cand, ctrl):
    """Mean over common (map, opponent) cells of share(cand) − share(ctrl), native, live maps."""
    cells = {cand: defaultdict(list), ctrl: defaultdict(list)}
    for r in ledger:
        if r['mode'] != 'native':
            continue
        for me, bot in (('a', r['bot_a']), ('b', r['bot_b'])):
            if bot in cells:
                opp = r['bot_b'] if me == 'a' else r['bot_a']
                cells[bot][(r['map'], opp)].append((r[me + '_wins'] or 0) + 0.5 * (r['draws'] or 0))
    common = set(cells[cand]) & set(cells[ctrl])
    if not common:
        return None
    deltas = [sum(cells[cand][k]) / len(cells[cand][k]) - sum(cells[ctrl][k]) / len(cells[ctrl][k]) for k in common]
    return dict(cells=len(common), delta=round(sum(deltas) / len(deltas), 3))


def fit_model(points):
    """Least squares live = a + b·local; returns dict(kind, n, a, b, resid_sd, mean_live)."""
    if len(points) < MIN_MODEL_POINTS:
        mean_live = round(statistics.mean(p[1] for p in points), 3) if points else None
        return dict(kind='band_mean', n=len(points), a=mean_live, b=0.0, resid_sd=None, mean_live=mean_live,
                    note=f'fewer than {MIN_MODEL_POINTS} sources with >= {MIN_MODEL_LIVE} live and >= {MIN_MODEL_LOCAL} local games: expect the mean live share regardless of the local number')
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    sd = statistics.pstdev(resid) if len(resid) > 1 else None
    return dict(kind='linear', n=len(points), a=round(a, 3), b=round(b, 3), resid_sd=round(sd, 3) if sd is not None else None, mean_live=round(my, 3))


def expected_live(model, local_share):
    if model is None or local_share is None or model.get('a') is None:
        return None
    return round(model['a'] + model['b'] * local_share, 3)


def run(conn, root, cfg, experiments, actor='hub/calibration'):
    repo = cfg['paths']['repo']
    summary = dict(rows_added=0, sources=[], model=None, skipped=None, expectations={})
    ledger = load_ledger(repo)
    if ledger is None:
        summary['skipped'] = 'no PyArrow or no game_stats.parquet in the repository'
        return summary
    index = bot_index(repo)
    sources = source_map(conn, index)
    at = db.now_iso()
    points = []
    for sub, (fp, bot, name) in sorted(sources.items()):
        loc = local_profile(ledger, bot)
        live = live_profile(conn, sub)
        entry = dict(submission=sub, candidate=name, bot=bot, local=loc and dict(n=loc['n'], share=loc['share'], share_ref=loc['share_ref'], n_ref=loc['n_ref'], opponents=loc['opponents']),
                     live=live and dict(n=live['n'], share=live['share'], opponents=live['opponents']))
        if loc and live and loc['n'] >= MIN_LOCAL and live['n'] >= MIN_LIVE:
            dis = round(100 * (live['share'] - loc['share']), 1)
            entry['disagreement_pp'] = dis
            map_dis = {m: round(100 * (live['by_map'][m] - loc['by_map'][m]), 0) for m in live['by_map'] if m in loc['by_map']}
            entry['map_disagreement_pp'] = map_dis
            prev = last_row(conn, fp, 'absolute')
            if not prev or prev['live_n'] != live['n'] or prev['local_n'] != loc['n']:
                conn.execute('INSERT INTO calibration(at,fingerprint,control_fingerprint,measure,local_panel,local_mode,local_toolkit,local_value,local_n,live_pool,live_value,live_n,disagreement,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                             (at, fp, None, 'absolute', f'ledger:live-maps:all-opponents({loc["opponents"]})', 'native', ','.join(loc['toolkits'])[:60], loc['share'], loc['n'],
                              f'field-controlled:{live["opponents"]} opponents', live['share'], live['n'], dis,
                              db.j(dict(bot=bot, submission=sub, share_ref=loc['share_ref'], n_ref=loc['n_ref'], map_disagreement_pp=map_dis))))
                summary['rows_added'] += 1
            if live['n'] >= MIN_MODEL_LIVE and loc['n'] >= MIN_MODEL_LOCAL:
                points.append((loc['share'], live['share']))
        summary['sources'].append(entry)
    model = fit_model(points)
    summary['model'] = model
    db.kv_set(conn, 'calibration_model', dict(at=at, **model))
    # handoff A1 additions: live-side opponent fingerprints and the local-priority gate
    try:
        from . import analysis as _analysis
        summary['opponents'] = opponent_fingerprints(_analysis.load_games(conn))
    except Exception:
        summary['opponents'] = []
    try:
        _paired = [dict(r) for r in conn.execute("SELECT local_value, live_value FROM calibration WHERE measure='paired'")]
        summary['local_priority'] = local_priority_ok(_paired)
    except Exception:
        summary['local_priority'] = None
    # paired rows for running experiments whose arms both map to local bots
    for e in experiments:
        if e.get('status') != 'running':
            continue
        cand, ctrl = sources.get(e.get('candidate')), sources.get(e.get('control'))
        if not (cand and ctrl):
            continue
        local = paired_local(ledger, cand[1], ctrl[1])
        live_blocks = [b for b in db.rows(conn, "SELECT decision FROM experiments WHERE id=?", (e['id'],))]
        live_delta, live_n = None, 0
        try:
            dec = json.loads(live_blocks[0]['decision']) if live_blocks and live_blocks[0]['decision'] else {}
            complete = [b for b in dec.get('pairs', []) if b.get('complete') and b.get('delta') is not None]
            if complete:
                live_delta = round(sum(b['delta'] for b in complete) / len(complete), 3)
                live_n = len(complete)
        except (ValueError, TypeError):
            pass
        if local and live_delta is not None:
            prev = last_row(conn, cand[0], 'paired', ctrl[0])
            if not prev or prev['live_n'] != live_n or prev['local_n'] != local['cells']:
                conn.execute('INSERT INTO calibration(at,fingerprint,control_fingerprint,measure,local_panel,local_mode,local_toolkit,local_value,local_n,live_pool,live_value,live_n,disagreement,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                             (at, cand[0], ctrl[0], 'paired', 'ledger:live-maps:common-cells', 'native', '', local['delta'], local['cells'], f'experiment:{e["id"][:8]}:complete-blocks', live_delta, live_n,
                              round(100 * (live_delta - local['delta']), 1), db.j(dict(candidate=cand[2], control=ctrl[2]))))
                summary['rows_added'] += 1
        if local:
            summary.setdefault('paired', []).append(dict(experiment=e['id'][:8], candidate=cand[1], control=ctrl[1], local=local, live_delta=live_delta, live_blocks=live_n))
    # expectations for queued candidates with local data but no live games yet
    for c in db.rows(conn, "SELECT name, fingerprint, status, submission_id FROM candidates WHERE status IN ('needs_runtime','runtime_ok','uploaded','registered')"):
        bot = index.get(c['fingerprint'])
        if not bot or (c['submission_id'] and (live_profile(conn, c['submission_id']) or {}).get('n', 0) >= MIN_LIVE):
            continue
        loc = local_profile(ledger, bot)
        if loc and loc['n'] >= MIN_LOCAL:
            summary['expectations'][c['name']] = dict(bot=bot, local_share=loc['share'], local_n=loc['n'], expected_live_share=expected_live(model, loc['share']))
    if summary['rows_added']:
        db.event(conn, root, actor, 'calibration_rows', dict(added=summary['rows_added'], model=model.get('kind')))
    return summary


def packet_lines(summary):
    if not summary:
        return ['- Calibration: not run']
    if summary.get('skipped'):
        return [f"- Calibration skipped: {summary['skipped']}"]
    L = []
    m = summary.get('model') or {}
    if m.get('kind') == 'linear':
        L.append(f"- Expectation model (n={m['n']} sources): live ≈ {m['a']} + {m['b']}·local, residual SD {m['resid_sd']}; mean live share {m['mean_live']}")
    else:
        L.append(f"- Expectation model: band mean {m.get('mean_live')} over n={m.get('n')} sources ({m.get('note', '')})")
    L.append('- Live vs local (live-pool maps, native ledger, all local opponents):')
    L.append('')
    L.append('| submission | bot | local n | local share | vs reference set | live n | live share | live − local (pp) |')
    L.append('|---|---|---|---|---|---|---|---|')
    for s in summary.get('sources', []):
        loc, live = s.get('local') or {}, s.get('live') or {}
        ref = f"{loc.get('share_ref')} (n={loc.get('n_ref')})" if loc.get('share_ref') is not None else '—'
        L.append(f"| {s['submission']} | {s['bot']} | {loc.get('n', 0)} | {loc.get('share', '—')} | {ref} | {live.get('n', 0)} | {live.get('share', '—')} | {s.get('disagreement_pp', '—')} |")
    for p in summary.get('paired', []):
        L.append(f"- Paired {p['experiment']}: local delta {p['local'] and p['local']['delta']} over {p['local'] and p['local']['cells']} common cells vs live delta {p['live_delta']} over {p['live_blocks']} complete blocks")
    for name, x in summary.get('expectations', {}).items():
        L.append(f"- Expectation for {name}: local {x['local_share']} (n={x['local_n']}) → expected live share {x['expected_live_share']}")
    for o in (summary.get('opponents') or [])[:6]:
        L.append(f"- Opponent {o['opponent']} (n={o['n']}): units r100 {o['units_r100']}, total r250 {o['total_r250']}, longest r499 {o['longest_r499']}, "
                 f"sonar/turn {o['sonar_per_turn']}, our share {o['our_share']}, their elim-of-us round {o['their_elim_round_med']}")
    lp = summary.get('local_priority')
    if lp and lp.get('n'):
        L.append(f"- Local-priority gate: {lp['n']} paired blocks, sign agreement {lp['agreement']}, allowed {lp['allowed']} ({lp['rule']})")
    return L[:36]


# --- handoff A1 additions (2026-09-28): opponent fingerprints, local-priority gate --------------------

def opponent_fingerprints(games):
    """Live-side behavioural fingerprint per opponent team from opponent_stages (handoff §3.5 starter):
    medians of their units r100, total r250, longest r400/r499, splits r100, portal steps, sonar per
    turn, over verified controlled field games, plus our win share and the median round at which they
    eliminated us. Stratifies nothing else — opponents pool their submissions (mixing is stated here)."""
    from . import analysis
    cells = defaultdict(list)
    for g in games:
        if g.get('verified') and g.get('origin') == 'controlled' and g.get('pool') == 'field':
            cells[g['opponent_team']].append(g)
    out = []
    for opp, rows in sorted(cells.items()):
        def m(fn, nd=1):
            vals = [fn(r) for r in rows]
            vals = [v for v in vals if v is not None]
            return round(statistics.median(vals), nd) if vals else None
        so = [analysis.opp_stage(r, 499, 'sonar') / analysis.opp_stage(r, 499, 'turns')
              for r in rows if analysis.opp_stage(r, 499, 'turns')]
        elim = [r.get('rounds') for r in rows if (r.get('score') or 0) == 0 and r.get('reason') == 'elimination']
        out.append(dict(opponent=opp, n=len(rows),
                        units_r100=m(lambda r: analysis.opp_stage(r, 100, 'units'), 0),
                        total_r250=m(lambda r: analysis.opp_stage(r, 250, 'total'), 0),
                        longest_r400=m(lambda r: analysis.opp_stage(r, 400, 'longest'), 0),
                        longest_r499=m(lambda r: analysis.opp_stage(r, 499, 'longest'), 0),
                        splits_r100=m(lambda r: analysis.opp_stage(r, 100, 'splits'), 0),
                        portal_steps=m(lambda r: analysis.opp_stage(r, 499, 'portal_steps'), 0),
                        sonar_per_turn=round(statistics.median(so), 2) if so else None,
                        our_share=round(sum(r.get('score') or 0 for r in rows) / len(rows), 2),
                        their_elim_round_med=round(statistics.median(elim)) if elim else None))
    return out


def local_priority_ok(paired_rows, min_pairs=10, min_agreement=0.7):
    """Gate for 'local paired deltas may enter the priority score' (handoff §3.4): paired
    sign agreement >= min_agreement over >= min_pairs measured experiment blocks.
    paired_rows: iterable of dicts with local_value and live_value (calibration 'paired' rows)."""
    pts = [(r['local_value'], r['live_value']) for r in paired_rows
           if r.get('local_value') is not None and r.get('live_value') is not None]
    n = len(pts)
    agree = sum(1 for lv, dv in pts if (lv > 0) == (dv > 0))
    return dict(n=n, agreement=round(agree / n, 2) if n else None,
                allowed=bool(n >= min_pairs and agree / n >= min_agreement if n else False),
                rule=f'>= {min_pairs} pairs with >= {min_agreement:.0%} sign agreement')
