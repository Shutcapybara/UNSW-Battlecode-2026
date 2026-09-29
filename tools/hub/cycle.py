"""The ten-minute evidence/decision cycle in observer mode, the tick summary and the two-hour review packet.

Observer mode (day one): no API calls. The legacy controller refreshes the API view every two minutes and persists it;
this cycle imports that record, re-derives every experiment verdict from stored games (a shadow check), scores the
candidate queue, computes diagnostics and ranked exposure, and writes `tick/<epoch>.json`, the review packet on
two-hour boundaries and the `hub-state` mirror in the repository.
"""
import json
import shutil
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from . import analysis, calibration, db, priority
from .legacy_import import import_legacy, lineage_of
from .stats import decision_v1, decision_v2, quota_used, timestamp

ATTENTION_KINDS = ('legacy_unreachable', 'legacy_worker_stale', 'legacy_needs_review', 'legacy_stopping', 'open_transaction',
                   'active_mismatch', 'shadow_disagreement', 'external_incumbent_change', 'quota_anomaly', 'contract_unevaluated')


def parse_iso(text):
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00')).timestamp()
    except Exception:
        return None


def legacy_shapes(conn):
    """Rebuild legacy-shaped blocks and results from hub rows so the ported decision functions can run unchanged."""
    blocks = []
    for b in db.rows(conn, 'SELECT * FROM blocks'):
        b = db.loads_row(b, 'map_ids', 'order_json', 'requests')
        blocks.append(dict(id=b['id'], phase=b['phase'], control=b['control_submission'], candidate=b['candidate_submission'], opponent=b['opponent_team'],
                           map_ids=b['map_ids'] or [], experiment=b['experiment_id'], requests=b['requests'] or [], excluded=b['excluded_reason']))
    results = {}
    for g in db.rows(conn, 'SELECT game_id, stats FROM games'):
        try:
            results[str(g['game_id'])] = json.loads(g['stats'])
        except (TypeError, ValueError):
            continue
    return blocks, results


def shadow_experiments(conn, root, actor, now):
    blocks, results = legacy_shapes(conn)
    out = []
    for e in db.rows(conn, 'SELECT * FROM experiments'):
        e = db.loads_row(e, 'decision', 'screen_opponents', 'confirmation_opponents', 'map_ids')
        mine = [b for b in blocks if b['experiment'] == e['id'] and not b.get('excluded')]
        fn = decision_v1 if e['protocol'] == 'v1' else decision_v2
        try:
            computed = fn(mine, results, e['alpha'] if e['protocol'] == 'v1' else 0.025)
        except Exception as exc:  # pragma: no cover
            computed = dict(verdict='error', error=repr(exc))
        legacy = (e.get('decision') or {}).get('verdict') if isinstance(e.get('decision'), dict) else None
        expected = e['verdict'] or legacy or ('screening' if e['status'] == 'running' else e['status'])
        agree = (computed.get('verdict') == expected) or (e['status'] == 'superseded_by_external_activation' and computed.get('verdict') in ('screening', 'confirming'))
        conn.execute('INSERT INTO shadow_checks(at,kind,subject,computed,legacy,agree) VALUES(?,?,?,?,?,?)',
                     (db.now_iso(), 'experiment_verdict', e['id'], db.j({k: v for k, v in computed.items() if k != 'pairs'}), db.j(dict(status=e['status'], verdict=e['verdict'], legacy_decision=legacy)), int(agree)))
        complete = {p: sum(1 for x in computed.get('pairs', []) if x['phase'] == p and x['complete']) for p in ('screen', 'confirm')}
        net = sum(pp['delta'] for x in computed.get('pairs', []) if x['phase'] == 'screen' and x['complete'] for pp in x['pairs'])
        out.append(dict(id=e['id'], candidate=e['candidate_submission'], candidate_name=e['candidate_name'], control=e['control_submission'], protocol=e['protocol'],
                        status=e['status'], recorded_verdict=e['verdict'], computed_verdict=computed.get('verdict'), agree=agree,
                        complete_blocks=complete, screen_net=net, alpha=e['alpha']))
    return out


def candidate_view(conn, cfg, now):
    inc = db.kv_get(conn, 'incumbent')
    if db.kv_get(conn, 'legacy_adopted') and db.kv_get(conn, 'control') is not None:
        inc = db.kv_get(conn, 'control')   # after the cutover the executor's control is the incumbent
    subs = {s['id']: s for s in db.rows(conn, 'SELECT * FROM submissions')}
    inc_name = subs.get(inc, {}).get('name', '') if inc else ''
    inc_lineage = lineage_of(inc_name) if inc_name else ''
    exps = db.rows(conn, 'SELECT * FROM experiments')
    cands = [db.loads_row(c, 'source_files', 'activation_contract', 'local_evidence') for c in db.rows(conn, 'SELECT * FROM candidates')]
    by_sub = {c['submission_id']: c for c in cands if c.get('submission_id')}
    lineage_last_live, lineage_rejected = {}, defaultdict(set)
    for e in exps:
        c = by_sub.get(e['candidate_submission'])
        if not c:
            continue
        when = parse_iso(e.get('opened_at') or e.get('created_at') or '') or 0
        lineage_last_live[c['lineage']] = max(lineage_last_live.get(c['lineage'], 0), when)
        if (e['verdict'] or '').startswith('reject') or (e['verdict'] or '').startswith('strategy_lost'):
            lineage_rejected[c['lineage']].add((c.get('mechanism') or '').strip().lower())
    live_games = defaultdict(int)
    for g in db.rows(conn, "SELECT own_submission, COUNT(*) n FROM games WHERE origin='controlled' AND verified=1 GROUP BY own_submission"):
        c = by_sub.get(g['own_submission'])
        if c:
            live_games[c['lineage']] += g['n']
    probes = {}
    for p in db.rows(conn, 'SELECT candidate_name, fingerprint, max_points, p99_points, passed, toolkit_version FROM probes'):
        cur = probes.setdefault(p['candidate_name'], dict(max_points=0, p99_points=0, passed=True, toolkit=p['toolkit_version'], n=0))
        cur['max_points'] = max(cur['max_points'], p['max_points'] or 0)
        cur['p99_points'] = max(cur['p99_points'], p['p99_points'] or 0)
        cur['passed'] = cur['passed'] and bool(p['passed'])
        cur['n'] += 1
    live_max = {}
    for g in db.rows(conn, 'SELECT own_submission, MAX(cpu_max) m FROM games WHERE verified=1 GROUP BY own_submission'):
        live_max[g['own_submission']] = g['m']
    for c in cands:
        if c.get('submission_id') in live_max:
            probes.setdefault(c['name'], {})['live_max'] = live_max[c['submission_id']]
    dev = defaultdict(lambda: dict(n=0, faults=0, cpu_max=0, opponents=set(), maps=set()))
    for g in db.rows(conn, "SELECT own_submission, opponent_team, map_id, faults, caught_errors, cpu_max FROM games WHERE pool='dev' AND verified=1"):
        d = dev[g['own_submission']]
        d['n'] += 1
        d['faults'] += (g['faults'] or 0) + (g['caught_errors'] or 0)
        d['cpu_max'] = max(d['cpu_max'], g['cpu_max'] or 0)
        d['opponents'].add(g['opponent_team'])
        d['maps'].add(g['map_id'])
    finding_ids = {f['id'] for f in db.rows(conn, 'SELECT id FROM findings')}
    ctx = dict(now=now, incumbent_lineage=inc_lineage, lineage_last_live=lineage_last_live, lineage_live_games=live_games,
               lineage_rejected_mechanisms=lineage_rejected, probes=probes, finding_ids=finding_ids, disagreements={}, local_z={})
    view = []
    for c in cands:
        s, terms = priority.score(c, ctx)
        d = dev.get(c.get('submission_id'))
        view.append(dict(name=c['name'], lineage=c['lineage'], status=c['status'], retired_reason=c.get('retired_reason'), legacy_status=c.get('legacy_status'),
                         legacy_parent=c.get('legacy_parent_submission'), control_policy=c.get('control_policy'), submission=c.get('submission_id'),
                         legacy_priority=c.get('priority'), hub_score=s, terms=terms, probe=probes.get(c['name']),
                         dev=dict(n=d['n'], faults=d['faults'], cpu_max=d['cpu_max'], maps=len(d['maps']), opponents=len(d['opponents'])) if d else None,
                         contract=(c.get('activation_contract') or {}).get('kind'), tried=c.get('submission_id') in {e['candidate_submission'] for e in exps}))
    view.sort(key=lambda v: (-(v['legacy_priority'] or 0), -v['hub_score']))
    return dict(incumbent=inc, incumbent_name=inc_name, incumbent_owner=subs.get(inc, {}).get('owner'), incumbent_lineage=inc_lineage, candidates=view)


def diagnostics(conn):
    rows = db.rows(conn, "SELECT own_submission s, opponent_team o, pool, origin, COUNT(*) n, AVG(score) share, SUM(faults) faults, MAX(cpu_max) cpu FROM games WHERE verified=1 GROUP BY own_submission, opponent_team, pool, origin")
    table = defaultdict(list)
    for r in rows:
        table[r['s']].append(dict(opponent=r['o'], pool=r['pool'], origin=r['origin'], n=r['n'], share=round(r['share'], 2) if r['share'] is not None else None, faults=r['faults'], cpu_max=r['cpu']))
    unverified = db.rows(conn, "SELECT game_id, own_submission, error FROM games WHERE verified=0 ORDER BY game_id DESC LIMIT 20")
    return dict(by_submission={str(k): v for k, v in table.items()}, unverified=unverified, unverified_count=conn.execute('SELECT COUNT(*) FROM games WHERE verified=0').fetchone()[0])


def ranked_exposure(conn, root, actor):
    """Ranked games played by executor-owned uploads (temporary activations caught by autoscrims or incoming challenges)."""
    executor = {s['id'] for s in db.rows(conn, "SELECT id FROM submissions WHERE owner='executor'")}
    added = []
    for s in db.rows(conn, 'SELECT series_id, payload FROM series'):
        try:
            payload = json.loads(s['payload'])
        except (TypeError, ValueError):
            continue
        m = payload.get('match', {})
        if not m.get('ranked'):
            continue
        ours = m.get('submissionAId') if m.get('teamAId') == 7 else m.get('submissionBId')
        elo = m.get('eloChangeA') if m.get('teamAId') == 7 else m.get('eloChangeB')
        if ours in executor:
            for g in payload.get('games', []):
                if not conn.execute('SELECT 1 FROM ranked_exposure WHERE game_id=?', (int(g['id']),)).fetchone():
                    db.upsert(conn, 'ranked_exposure', dict(game_id=int(g['id']), series_id=str(s['series_id']), submission=ours, elo_change=elo,
                                                            overlapped_activation=m.get('requestedAt'), note='executor-owned upload played ranked'), 'game_id')
                    added.append(int(g['id']))
    total = conn.execute('SELECT COUNT(*) n, SUM(elo_change) elo FROM ranked_exposure').fetchone()
    return dict(added=added, games=total['n'], elo_sum=total['elo'])


def run_cycle(root, cfg, actor='hub/cycle', force_packet=False, now=None):
    root = Path(root)
    now = now or time.time()
    conn = db.connect(root)
    tick = dict(at=db.now_iso(), epoch=int(now), cycle='600s', mode='observer', attention=[], external_actions=[], decisions=[], dispatched=[],
                deferred=[dict(reason='observer mode: dispatch stays with the legacy executor until cutover')])
    live = Path(cfg['paths']['legacy_live'])
    last_cycle_at = db.kv_get(conn, 'last_cycle_at')
    adopted = db.kv_get(conn, 'legacy_adopted')
    if adopted:
        tick['imported'] = dict(frozen_at=adopted.get('at'), note='legacy record adopted at cutover; the executor ledger is authoritative (hubctl executor release-legacy to resume imports)')
        manifest = None
    elif not (live / 'state/state.json').exists():
        tick['attention'].append(dict(kind='legacy_unreachable', detail=str(live)))
        manifest = None
    else:
        manifest = import_legacy(conn, root, live, actor=actor)
        tick['imported'] = dict(counts=manifest['counts'], checks=manifest['checks'])
    # --- safety -----------------------------------------------------------------------------------------
    rs = db.kv_get(conn, 'legacy_runner_status') or {}
    rc = db.kv_get(conn, 'legacy_restoration_check') or {}
    open_tx = db.kv_get(conn, 'legacy_open_transactions') or {}
    at = parse_iso(rs.get('at', '') or '')
    tick['legacy_worker'] = dict(state=rs.get('state'), at=rs.get('at'), age_seconds=round(now - at) if at else None, jobs=list((rs.get('jobs') or {}).keys()),
                                 attention=(rs.get('attention') or {}).get('reason'), plan_expires=rs.get('plan_expires_epoch'))
    retired = bool(adopted)   # after the cutover the legacy worker is retired by design: its silence is not attention
    if retired:
        tick['legacy_worker']['retired'] = 'adopted at cutover; the hub executor is live'
    if at and now - at > cfg['legacy']['stale_seconds'] and not retired:
        tick['attention'].append(dict(kind='legacy_worker_stale', detail=f'runner_status.json is {round(now - at)} s old'))
    if rs.get('state') == 'needs_review' and not retired:
        tick['attention'].append(dict(kind='legacy_needs_review', detail=(rs.get('attention') or {}).get('reason')))
    if rs.get('state') == 'stopping' and not retired:
        tick['attention'].append(dict(kind='legacy_stopping', detail='the legacy worker is draining and will exit; kickstart needed unless intentional'))
    if open_tx and not retired:
        tick['attention'].append(dict(kind='open_transaction', detail=list(open_tx.keys())))
    tick['active_submission'] = rc.get('active')
    tick['expected'] = rc.get('expected')
    tick['restoration_matched'] = rc.get('matched')
    tick['restoration_checked_at'] = rc.get('at')
    last = db.kv_get(conn, 'executor_last') or {}
    if adopted and last.get('active') is not None:
        # once the executor is live its snapshot is the truth; the legacy restoration check is a frozen file
        tick['active_submission'] = last.get('active')
        tick['expected'] = db.kv_get(conn, 'control')
        tick['restoration_matched'] = last.get('active') == db.kv_get(conn, 'control')
        tick['restoration_checked_at'] = last.get('at')
    if rc and not rc.get('matched'):
        tick['attention'].append(dict(kind='active_mismatch', detail=dict(active=rc.get('active'), expected=rc.get('expected'))))
    # --- external actions since the last cycle ------------------------------------------------------------
    since = last_cycle_at or '1970'
    for x in db.rows(conn, 'SELECT * FROM external_actions WHERE at>? ORDER BY at', (since,)):
        tick['external_actions'].append(dict(at=x['at'], kind=x['kind'], submission=x['submission'], previous=x['previous'], note=x['note']))
    if tick['external_actions']:
        tick['attention'].append(dict(kind='external_incumbent_change', detail=[x['submission'] for x in tick['external_actions']]))
    # --- quota -----------------------------------------------------------------------------------------
    q = db.kv_get(conn, 'legacy_quota_used') or {}
    qa = parse_iso(q.get('updated') or '') if q else None
    tick['quota'] = dict(legacy=q.get('quota'), as_of=q.get('updated'), age_seconds=round(now - qa) if qa else None,
                         hourly=cfg['budget']['hourly_games'], executor_cap=cfg['budget']['executor_cap'])
    # --- experiments (shadow re-derivation) ---------------------------------------------------------------
    tick['experiments'] = shadow_experiments(conn, root, actor, now)
    for e in tick['experiments']:
        if not e['agree']:
            tick['attention'].append(dict(kind='shadow_disagreement', detail=dict(experiment=e['id'], computed=e['computed_verdict'], recorded=e['recorded_verdict'] or e['status'])))
    # --- queue -----------------------------------------------------------------------------------------
    view = candidate_view(conn, cfg, now)
    tick.update(incumbent=view['incumbent'], incumbent_name=view['incumbent_name'], incumbent_owner=view['incumbent_owner'])
    tick['queue'] = [c for c in view['candidates'] if c['status'] not in ('retired', 'runtime_failed')]
    tick['retired'] = [dict(name=c['name'], reason=c['retired_reason'] or c['status']) for c in view['candidates'] if c['status'] in ('retired', 'runtime_failed')]
    for c in tick['queue']:
        if c['contract'] in ('behavioural_signature', 'divergence_window'):
            tick['attention'].append(dict(kind='contract_unevaluated', detail=c['name']))
    plan = db.kv_get(conn, 'legacy_two_hour_plan') or {}
    tick['plan'] = dict(incumbent=plan.get('incumbent'), expires=plan.get('expires_epoch'), candidates=[c['name'] for c in plan.get('candidates', [])],
                        tasks=[dict(kind=t.get('kind'), candidate=t.get('candidate'), opponent=t.get('opponent')) for t in plan.get('tasks', [])],
                        screen=(plan.get('decision_rules') or {}).get('screen_opponents'), confirmation=(plan.get('decision_rules') or {}).get('confirmation_opponents'))
    # --- diagnostics and exposure --------------------------------------------------------------------------
    tick['diagnostics'] = diagnostics(conn)
    try:
        tick['analysis'] = analysis.run(conn, tick['experiments'])
    except Exception as exc:  # analysis must never stop the cycle
        tick['analysis'] = dict(error=repr(exc)[:200], profiles={}, opponents=[], contrasts={})
    try:
        tick['calibration'] = calibration.run(conn, root, cfg, tick['experiments'], actor=actor)
    except Exception as exc:  # calibration must never stop the cycle
        tick['calibration'] = dict(skipped='error: ' + repr(exc)[:160], sources=[], expectations={})
    tick['ranked_exposure'] = ranked_exposure(conn, root, actor)
    tick['findings_since'] = db.rows(conn, 'SELECT id, kind, title, author, at FROM findings WHERE at>? ORDER BY at', (since,))
    tick['open_tasks'] = db.rows(conn, "SELECT id, kind, title, priority FROM tasks WHERE status='open' ORDER BY priority DESC, id")
    tick['storage'] = storage_report(root)
    tick['review_responses'] = ingest_responses(conn, root, cfg, actor)
    tick['attention_count'] = len(tick['attention'])
    # --- persist ----------------------------------------------------------------------------------------
    (root / 'tick').mkdir(parents=True, exist_ok=True)
    (root / 'tick' / f'{int(now)}.json').write_text(db.j(tick))
    (root / 'tick' / 'latest.json').write_text(db.j(tick))
    conn.execute('INSERT OR REPLACE INTO ticks(epoch,at,payload) VALUES(?,?,?)', (int(now), tick['at'], db.j({k: v for k, v in tick.items() if k != 'diagnostics'})))
    db.kv_set(conn, 'last_cycle_at', tick['at'])
    db.event(conn, root, actor, 'cycle', dict(epoch=int(now), attention=[a['kind'] for a in tick['attention']], queue=len(tick['queue'])))
    # --- packet on the two-hour boundary -------------------------------------------------------------------
    last_packet = db.kv_get(conn, 'last_packet_epoch') or 0
    boundary = int(now // cfg['cadence']['review_every_seconds']) * cfg['cadence']['review_every_seconds']
    if force_packet or last_packet < boundary:
        path = write_packet(conn, root, cfg, tick, int(now))
        tick['packet'] = str(path)
        (root / 'tick' / 'latest.json').write_text(db.j(tick))
    mirror(conn, root, cfg, tick)
    conn.close()
    return tick


def ingest_responses(conn, root, cfg, actor):
    """Record director responses written into the mirror (`hub-state/review/response-<epoch>.md`) by sessions without hub access."""
    out = []
    review = Path(cfg['paths']['mirror']) / 'review'
    if not review.exists():
        return out
    seen = {r['body'][:64] for r in db.rows(conn, 'SELECT body FROM review_responses')}
    for path in sorted(review.glob('response-*.md')):
        try:
            epoch = int(path.stem.split('-')[1])
        except (IndexError, ValueError):
            continue
        body = path.read_text()
        if conn.execute('SELECT 1 FROM review_responses WHERE packet_epoch=? AND body=?', (epoch, body)).fetchone():
            continue
        conn.execute('INSERT INTO review_responses(at,packet_epoch,actor,body) VALUES(?,?,?,?)', (db.now_iso(), epoch, 'director/mirror', body))
        shutil.copy2(path, Path(root) / 'review' / path.name)
        db.event(conn, root, actor, 'review_response_ingested', dict(packet_epoch=epoch, path=str(path), lines=body.count('\n') + 1))
        out.append(dict(packet_epoch=epoch, path=str(path)))
    return out


def storage_report(root):
    total = 0
    biggest = []
    for child in Path(root).iterdir():
        size = sum(f.stat().st_size for f in child.rglob('*') if f.is_file()) if child.is_dir() else child.stat().st_size
        total += size
        biggest.append((size, child.name))
    biggest.sort(reverse=True)
    return dict(total_mb=round(total / 1e6, 1), largest=[dict(name=n, mb=round(s / 1e6, 1)) for s, n in biggest[:5]])


def fmt_pct(x):
    return '—' if x is None else f'{100 * x:.0f}%'


def write_packet(conn, root, cfg, tick, epoch):
    """Two-hour review packet, ≤ 300 lines (Part B §5.5)."""
    root = Path(root)
    last_epoch = db.kv_get(conn, 'last_packet_epoch') or 0
    since = datetime.fromtimestamp(last_epoch, timezone.utc).isoformat() if last_epoch else '1970'
    L = []
    L.append(f"# JKS hub review packet — {tick['at']} (epoch {epoch}, observer mode)")
    L.append('')
    L.append('Read `docs/hub/DIRECTOR.md` for the turn procedure. Respond with `hubctl review respond --packet ' + str(epoch) + ' --body response.md`.')
    L.append('')
    L.append('## 0. Safety')
    L.append(f"- Active submission {tick.get('active_submission')} / expected {tick.get('expected')} / matched **{tick.get('restoration_matched')}** at {tick.get('restoration_checked_at')}")
    L.append(f"- Incumbent (control) **{tick.get('incumbent')}** {tick.get('incumbent_name')!r} owner={tick.get('incumbent_owner')}")
    w = tick['legacy_worker']
    L.append(f"- Legacy worker: state **{w['state']}**, status age {w['age_seconds']} s, jobs {w['jobs']}, attention {w['attention']!r}, plan expires {w['plan_expires']}")
    q = tick['quota']
    L.append(f"- Quota (legacy rolling hour, as of {q['as_of']}): {q['legacy']} of {q['hourly']} (executor cap {q['executor_cap']})")
    L.append(f"- Attention flags: {', '.join(sorted({a['kind'] for a in tick['attention']})) or 'none'}")
    L.append('')
    L.append('## 1. Changes since the last packet')
    dec = db.rows(conn, 'SELECT at, experiment_id, verdict, protocol, source FROM decisions WHERE at>? ORDER BY at', (since,))
    L.append(f"- Verdicts: " + ('; '.join(f"{d['experiment_id'][:8]} → {d['verdict']} ({d['protocol']}, {d['source']}) at {d['at'][11:19]}Z" for d in dec) if dec else 'none'))
    ext = db.rows(conn, 'SELECT at, kind, submission, previous, note FROM external_actions WHERE at>? ORDER BY at', (since,))
    L.append(f"- External actions: " + ('; '.join(f"{x['at'][11:19]}Z {x['kind']} {x['previous']}→{x['submission']} ({x['note']})" for x in ext) if ext else 'none'))
    new_c = db.rows(conn, 'SELECT name, lineage, status, registered_by FROM candidates WHERE registered_at>? ORDER BY registered_at', (since,))
    L.append(f"- New candidates: " + ('; '.join(f"{c['name']} [{c['lineage']}] {c['status']} by {c['registered_by']}" for c in new_c) if new_c else 'none'))
    ups = db.rows(conn, 'SELECT name, submission_id, upload_name FROM candidates WHERE submission_id IS NOT NULL AND updated_at>? ORDER BY submission_id', (since,))
    L.append(f"- Uploads seen: " + ('; '.join(f"{u['name']}={u['submission_id']}" for u in ups) if ups else 'none'))
    L.append(f"- Retired: " + ('; '.join(f"{r['name']} ({r['reason']})" for r in tick['retired']) if tick['retired'] else 'none'))
    g = db.kv_get(conn, 'git_last_sync') or {}
    L.append(f"- Git (last sync {g.get('at', 'never')[:16]}): committed {len(g.get('committed', []))}, skipped {len(g.get('skipped', []))}, merged {g.get('merged')}, pushed {g.get('pushed')}, ahead {g.get('ahead')} behind {g.get('behind')}"
             + ('; attention: ' + '; '.join(g['attention']) if g.get('attention') else '') + ('; errors: ' + '; '.join(g['errors'])[:160] if g.get('errors') else ''))
    L.append('')
    L.append('## 2. Failures and anomalies')
    if tick['attention']:
        for a in tick['attention']:
            L.append(f"- **{a['kind']}**: {json.dumps(a['detail'], default=str)[:200]}")
    else:
        L.append('- none')
    d = tick['diagnostics']
    L.append(f"- Unverified games: {d['unverified_count']}" + (' — ' + '; '.join(f"{u['game_id']} ({(u['error'] or '')[:60]})" for u in d['unverified'][:5]) if d['unverified'] else ''))
    failed = db.rows(conn, 'SELECT candidate_name, map_id, side, max_points, p99_points, faults, error, toolkit_version FROM probes WHERE passed=0 ORDER BY at DESC LIMIT 8')
    L.append(f"- Failed probes: " + ('; '.join(f"{p['candidate_name']} {p['map_id']}{p['side']} max {p['max_points']} p99 {p['p99_points']} faults {p['faults']} {p['error'] or ''} [{p['toolkit_version']}]" for p in failed) if failed else 'none'))
    L.append(f"- Ranked exposure of executor uploads: {tick['ranked_exposure']['games']} games, Elo sum {tick['ranked_exposure']['elo_sum']}")
    L.append('')
    L.append('## 3. Contradictions')
    dis = [e for e in tick['experiments'] if not e['agree']]
    L.append(f"- Shadow re-derivation disagreements: " + ('; '.join(f"{e['id'][:8]} computed {e['computed_verdict']} vs recorded {e['recorded_verdict'] or e['status']}" for e in dis) if dis else 'none (every stored verdict re-derives from stored games)'))
    cal = db.rows(conn, 'SELECT fingerprint, measure, disagreement, local_panel, live_pool, note FROM calibration WHERE ABS(disagreement)>15 ORDER BY at DESC LIMIT 8')
    L.append(f"- Local/live disagreements > 15 pp: " + ('; '.join(f"{c['fingerprint'][:8]} {c['measure']} {c['disagreement']:+.0f} pp" for c in cal) if cal else 'none recorded'))
    L.extend(calibration.packet_lines(tick.get('calibration')))
    excl = db.rows(conn, 'SELECT id, phase, opponent_team, excluded_reason FROM blocks WHERE excluded_reason IS NOT NULL ORDER BY created_at DESC LIMIT 6')
    L.append(f"- Excluded blocks: " + ('; '.join(f"{b['id'][:8]} {b['phase']} vs {b['opponent_team']}: {b['excluded_reason'][:60]}" for b in excl) if excl else 'none'))
    unev = [c['name'] for c in tick['queue'] if c['contract'] in ('behavioural_signature', 'divergence_window')]
    L.append(f"- Contracts not evaluable yet: {', '.join(unev) or 'none'}")
    L.append('')
    L.append('## 4. Prioritized evidence')
    fnd = db.rows(conn, "SELECT id, kind, title, author, at, evidence_refs FROM findings WHERE status='published' ORDER BY at DESC LIMIT 5")
    if fnd:
        for f in fnd:
            n = len(json.loads(f['evidence_refs'] or '[]'))
            L.append(f"- {f['id']} [{f['kind']}] {f['title']} — {f['author']}, {f['at'][:16]}Z, {n} refs")
    else:
        L.append('- no findings published yet')
    L.extend(analysis.packet_lines(tick.get('analysis') or dict(profiles={}, contrasts={}), tick.get('incumbent')))
    L.append('- Live controlled win shares by submission (A-side, verified):')
    L.append('')
    L.append('| submission | opponent | pool | n | share | faults | cpu max |')
    L.append('|---|---|---|---|---|---|---|')
    count = 0
    for sub, rows_ in sorted(d['by_submission'].items(), key=lambda kv: -int(kv[0]) if kv[0].isdigit() else 0):
        for r in sorted(rows_, key=lambda r: (-r['n'])):
            if r['origin'] != 'controlled' or count >= 30:
                continue
            L.append(f"| {sub} | {r['opponent']} | {r['pool']} | {r['n']} | {fmt_pct(r['share'])} | {r['faults']} | {r['cpu_max']} |")
            count += 1
    L.append('')
    L.append('## 5. Queue and plan')
    L.append('')
    L.append('| candidate | lineage | status | legacy prio | hub score | probe max/p99 | dev n/faults/cpu | contract | notes |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for c in tick['queue'][:20]:
        p = c.get('probe') or {}
        dv = c.get('dev') or {}
        notes = []
        if c.get('tried'):
            notes.append('tried')
        if c['terms'].get('already_rejected_same_mechanism'):
            notes.append('REJECTED-MECHANISM')
        if c.get('control_policy') == 'current':
            notes.append('follows control')
        elif c.get('legacy_parent') and c.get('legacy_parent') != tick.get('incumbent'):
            notes.append(f"orphaned (parent {c['legacy_parent']})")
        L.append(f"| {c['name']} | {c['lineage']} | {c['status']} | {c['legacy_priority']} | {c['hub_score']} | {p.get('max_points') or '—'}/{p.get('p99_points') or '—'} | {dv.get('n', 0)}/{dv.get('faults', 0)}/{dv.get('cpu_max', 0)} | {c['contract']} | {', '.join(notes)} |")
    L.append('')
    pl = tick['plan']
    L.append(f"- Legacy plan: incumbent {pl['incumbent']}, expires {pl['expires']}, candidates {pl['candidates']}")
    L.append(f"- Plan tasks: " + ('; '.join(f"{t['kind']}:{t['candidate']}" + (f"@{t['opponent']}" if t.get('opponent') else '') for t in pl['tasks']) if pl['tasks'] else 'none (queue empty)'))
    L.append(f"- Screen panel {pl['screen']}; confirmation panel {pl['confirmation']}")
    L.append(f"- Experiments: " + ('; '.join(f"{e['id'][:8]} {e['candidate']} vs {e['control']} {e['status']} [{e['protocol']}] screen {e['complete_blocks']['screen']}/3 net {e['screen_net']:+.0f}, confirm {e['complete_blocks']['confirm']}/12" for e in tick['experiments']) if tick['experiments'] else 'none'))
    L.append(f"- Open tasks: " + ('; '.join(f"{t['id']} {t['title'][:50]}" for t in tick['open_tasks'][:10]) if tick['open_tasks'] else 'none'))
    last_resp = db.rows(conn, 'SELECT at, packet_epoch, actor FROM review_responses ORDER BY id DESC LIMIT 1')
    L.append(f"- Last director response: " + (f"{last_resp[0]['at'][:16]}Z for packet {last_resp[0]['packet_epoch']} by {last_resp[0]['actor']}" if last_resp else 'none yet'))
    L.append(f"- Storage: {tick['storage']['total_mb']} MB in hub root; largest {tick['storage']['largest'][:3]}")
    L.append('')
    L.append('## 6. Decisions required (default if no response)')
    lines6 = []
    if any(a['kind'] == 'legacy_stopping' for a in tick['attention']):
        lines6.append('- The legacy worker is stopping; default: the actuator kickstarts it once it has exited (legacy.keepalive).')
    if any(a['kind'] == 'legacy_needs_review' for a in tick['attention']):
        lines6.append('- The legacy worker needs review; default: no new requests until a director clears it (`runner.py --clear-review` equivalent).')
    if not pl['tasks']:
        lines6.append('- The queue is empty; default: nothing is dispatched. Register a candidate (`hubctl candidate register` then `stage-live`).')
    if dis:
        lines6.append('- A stored verdict does not re-derive; default: keep the recorded verdict, open a correction finding.')
    orphans = [c['name'] for c in tick['queue'] if c.get('control_policy') != 'current' and c.get('legacy_parent') not in (None, tick.get('incumbent')) and c['status'] in ('uploaded', 'needs_runtime')]
    if orphans:
        lines6.append(f"- Orphaned legacy candidates {orphans}; default: leave orphaned (their evidence stays). Re-stage with `control_policy=current` only with a changed mechanism or a note.")
    L.extend(lines6 or ['- none'])
    text = '\n'.join(L[:300]) + '\n'
    (root / 'review').mkdir(parents=True, exist_ok=True)
    path = root / 'review' / f'packet-{epoch}.md'
    path.write_text(text)
    (root / 'review' / 'packet-latest.md').write_text(text)
    conn.execute('INSERT OR REPLACE INTO packets(epoch,at,path,lines) VALUES(?,?,?,?)', (epoch, tick['at'], str(path), text.count('\n')))
    db.kv_set(conn, 'last_packet_epoch', epoch)
    return path


def mirror(conn, root, cfg, tick):
    """Write the read-only `hub-state` mirror into the repository (Part B §4.5)."""
    out = Path(cfg['paths']['mirror'])
    (out / 'tick').mkdir(parents=True, exist_ok=True)
    (out / 'review').mkdir(parents=True, exist_ok=True)
    (out / '.gitignore').write_text('*\n')
    as_of = tick['at']
    (out / 'tick' / 'latest.json').write_text(db.j(tick))
    (out / 'status.json').write_text(db.j(dict(as_of=as_of, incumbent=tick.get('incumbent'), incumbent_name=tick.get('incumbent_name'), active=tick.get('active_submission'),
                                                 restoration_matched=tick.get('restoration_matched'), legacy_worker=tick['legacy_worker'], quota=tick['quota'],
                                                 attention=tick['attention'], queue=[dict(name=c['name'], status=c['status'], legacy_priority=c['legacy_priority'], hub_score=c['hub_score']) for c in tick['queue']],
                                                 experiments=tick['experiments'], plan=tick['plan'], git=db.kv_get(conn, 'git_last_sync'))))
    (out / 'candidates.json').write_text(db.j(dict(as_of=as_of, candidates=tick['queue'] + tick['retired'])))
    (out / 'experiments.json').write_text(db.j(dict(as_of=as_of, experiments=tick['experiments'])))
    with (out / 'decisions.jsonl').open('w') as handle:
        for d in db.rows(conn, 'SELECT * FROM decisions ORDER BY id'):
            handle.write(db.j(d) + '\n')
    (out / 'tasks.json').write_text(db.j(dict(as_of=as_of, tasks=[db.loads_row(t, 'spec') for t in db.rows(conn, 'SELECT * FROM tasks ORDER BY priority DESC, id')])))
    (out / 'findings.json').write_text(db.j(dict(as_of=as_of, findings=[db.loads_row(f, 'evidence_refs') for f in db.rows(conn, 'SELECT id, at, author, kind, title, body_path, evidence_refs, task_id, supersedes, status FROM findings ORDER BY at')])))
    (out / 'calibration.json').write_text(db.j(dict(as_of=as_of, rows=db.rows(conn, 'SELECT * FROM calibration ORDER BY at DESC LIMIT 500'))))
    latest = Path(root) / 'review' / 'packet-latest.md'
    if latest.exists():
        latest_target = out / 'review' / 'packet-latest.md'
        if latest.resolve() != latest_target.resolve():
            shutil.copy2(latest, latest_target)
        for p in sorted((Path(root) / 'review').glob('packet-*.md'))[-6:]:
            target = out / 'review' / p.name
            if p.resolve() != target.resolve():
                shutil.copy2(p, target)
    return out
