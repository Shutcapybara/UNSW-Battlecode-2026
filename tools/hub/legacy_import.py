"""Import the legacy live-validation record (`LIVE/`) into the hub, idempotently (Part B §11.3, Appendix B).

Read-only against `LIVE`. Every legacy status and verdict is kept verbatim (`legacy_status`, `protocol='v1'`).
Re-running is safe: rows are upserted by their legacy identities and the manifest counts are re-validated.
"""
import hashlib
import json
import re
import time
from pathlib import Path

from . import db
from .stats import quota_used

TERMINAL = {'reject_screen', 'reject_confirmation', 'promote', 'superseded_by_external_activation', 'measurement_invalid'}
LEGACY_STATUS = {  # legacy registry status -> (hub status, retired_reason)
    'needs_runtime': ('needs_runtime', None), 'uploaded': ('uploaded', None), 'incumbent': ('uploaded', None),
    'deferred_runtime_repair': ('retired', 'runtime_invalid'), 'retired_before_testing': ('retired', 'withdrawn_by_author'),
}


def read_json(path, default=None):
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else default


def lineage_of(name):
    stem = re.sub(r'[^a-z0-9-]+', '-', name.lower()).strip('-')
    stem = re.sub(r'^(?:(?:local|lv|hub)-)+', '', stem)
    stem = re.sub(r'-[0-9a-f]{8}-ai$', '', stem)
    stem = re.sub(r'-ai$', '', stem)
    m = re.match(r'([a-z][a-z0-9]*(?:-[a-z]+)*?)(?=-(?:v|x|t|s|m|b|c|d|f)\d)', stem)
    return m.group(1) if m else stem.split('-')[0]


def import_legacy(conn, root, live, actor='hub/import'):
    live = Path(live)
    state = read_json(live / 'state/state.json', {})
    registry = read_json(live / 'registry.json', [])
    config = read_json(live / 'config.json', {})
    submissions = read_json(live / 'state/submissions.json', [])
    manifest = dict(at=db.now_iso(), live=str(live), counts={}, checks={})
    # --- candidates -------------------------------------------------------------------------------------
    upload_names = {c.get('upload_name') for c in registry if c.get('upload_name')}
    for c in registry:
        status, reason = LEGACY_STATUS.get(c['status'], ('registered', None))
        gate = read_json(live / 'state/runtime' / c['name'] / 'gate.json', {})
        if status == 'needs_runtime' and gate.get('fingerprint') == c['fingerprint'] and gate.get('passed') is False:
            status, reason = 'runtime_failed', 'runtime_invalid'
        db.upsert(conn, 'candidates', dict(
            name=c['name'], fingerprint=c['fingerprint'], code_fingerprint=c['fingerprint'], archive_path=c.get('archive'),
            archive_sha256=c.get('archive_sha256'), source_files=c.get('files'), language='python', lineage=lineage_of(c['name']),
            author='legacy', lineage_parent_name=None, lineage_parent_fingerprint=None, source_ref='dir:' + (c.get('source') or ''),
            hypothesis=c.get('hypothesis'), mechanism=c.get('hypothesis'), expected_change=None,
            activation_contract={'kind': 'legacy_none'} if not c.get('activity_reference') else {'kind': 'legacy_activity', 'reference': c.get('activity_reference')},
            local_evidence={'path': c.get('local_evidence'), 'sha256': c.get('local_evidence_sha256')} if c.get('local_evidence') else None,
            priority=c.get('priority', 100), status=status, retired_reason=reason, submission_id=c.get('submission'),
            upload_name=c.get('upload_name'), api_source_hash=c.get('api_source_hash'), legacy_name=c['name'], legacy_status=c['status'],
            legacy_parent_submission=c.get('parent_submission'), control_policy=c.get('control_policy'),
            registered_by=c.get('registered_by', 'legacy'), registered_at=c.get('registered')), 'name')
    manifest['counts']['candidates'] = len(registry)
    # --- submissions ------------------------------------------------------------------------------------
    for s in submissions:
        name = s.get('name') or ''
        owner = 'executor' if (name in upload_names or re.match(r'^LV-.*-ai$', name)) else 'teammate'
        db.upsert(conn, 'submissions', dict(id=s['id'], name=name, source_hash=s.get('sourceHash'), language=s.get('language'),
                                            status=s.get('status'), first_seen=None, last_seen=db.now_iso(), owner=owner), 'id')
    manifest['counts']['submissions'] = len(submissions)
    # --- blocks and experiments -------------------------------------------------------------------------
    game_block = {}
    for b in state.get('blocks', []):
        for group in b.get('requests', []):
            for gid in group:
                game_block[int(gid)] = b
        db.upsert(conn, 'blocks', dict(id=b['id'], experiment_id=b.get('experiment'), phase=b.get('phase'),
                                       control_submission=b.get('control'), candidate_submission=b.get('candidate'),
                                       opponent_team=b.get('opponent'), map_ids=b.get('map_ids'), order_json=b.get('order'),
                                       requests=b.get('requests'), fill_attempts=b.get('fill_attempts', 0),
                                       excluded_reason=b.get('excluded') if isinstance(b.get('excluded'), str) else None), 'id')
    manifest['counts']['blocks'] = len(state.get('blocks', []))
    by_sub = {c.get('submission'): c['name'] for c in registry if c.get('submission')}
    exp_status = {}
    for e in state.get('experiments', []):
        exp_status[e['status']] = exp_status.get(e['status'], 0) + 1
        db.upsert(conn, 'experiments', dict(id=e['id'], candidate_name=by_sub.get(e.get('candidate')), candidate_submission=e.get('candidate'),
                                            control_submission=e.get('control'), protocol='v1', alpha=e.get('alpha'),
                                            screen_opponents=e.get('screen_opponents'), confirmation_opponents=e.get('confirmation_opponents'),
                                            map_ids=e.get('map_ids'), status=e['status'], verdict=e['status'] if e['status'] in TERMINAL else None,
                                            decision=e.get('decision'), frozen_reason='external activation' if e['status'] == 'superseded_by_external_activation' else None,
                                            source_fingerprint=e.get('source_fingerprint')), 'id')
    manifest['counts']['experiments'] = exp_status
    for i, d in enumerate(state.get('decisions', [])):
        db.upsert(conn, 'decisions', dict(id=i + 1, at=d.get('at'), experiment_id=d.get('experiment'), checkpoint='legacy',
                                          verdict=d.get('verdict'), detail=d, protocol='v1', source='legacy'), 'id')
    manifest['counts']['decisions'] = len(state.get('decisions', []))
    # --- requests ---------------------------------------------------------------------------------------
    req_counts = {}
    for i, r in enumerate(state.get('requests', [])):
        rid = hashlib.sha256(json.dumps([r.get('at'), r.get('pool'), r.get('opponent'), r.get('submission'), r.get('map_ids')], sort_keys=True).encode()).hexdigest()[:24]
        key = f"{r.get('pool')}/{r.get('status')}"
        req_counts[key] = req_counts.get(key, 0) + 1
        db.upsert(conn, 'requests', dict(id=rid, at=r.get('at'), pool=r.get('pool'), opponent_team=r.get('opponent'), submission=r.get('submission'),
                                         map_ids=r.get('map_ids'), count=r.get('count'), status=r.get('status'), game_ids=r.get('ids'),
                                         block_id=r.get('block'), origin=r.get('origin', 'controlled')), 'id')
    manifest['counts']['requests'] = req_counts
    # --- games ------------------------------------------------------------------------------------------
    series_ranked = {}
    for sid, payload in state.get('seen_series', {}).items():
        db.upsert(conn, 'series', dict(series_id=str(sid), payload=payload, fetched_at=db.now_iso()), 'series_id')
        m = payload.get('match', {}) if isinstance(payload, dict) else {}
        for g in payload.get('games', []) if isinstance(payload, dict) else []:
            series_ranked[int(g['id'])] = (m.get('ranked'), m.get('requestedBy'), m.get('eloChangeA'), m.get('eloChangeB'), m.get('seriesId'))
    manifest['counts']['series'] = len(state.get('seen_series', {}))
    origin_counts = {}
    for gid, r in state.get('results', {}).items():
        gid = int(gid)
        origin_counts[r.get('origin', 'controlled')] = origin_counts.get(r.get('origin', 'controlled'), 0) + 1
        b = game_block.get(gid, {})
        ranked = series_ranked.get(gid, (None,))[0]
        db.upsert(conn, 'games', dict(game_id=gid, series_id=r.get('series'), requested_at=r.get('requested'), ranked=ranked, pool=r.get('pool'),
                                      origin=r.get('origin', 'controlled'), own_submission=r.get('submission'), opponent_team=r.get('opponent'),
                                      opponent_submission=r.get('opponent_submission'), map_id=r.get('map_id'), map_name=r.get('map_name'),
                                      map_hash=r.get('map_hash'), api_side=r.get('side'), observed_side=r.get('observed_side', r.get('side')), seed=r.get('seed'),
                                      status='verified' if r.get('verified') else 'unverified', verified=int(bool(r.get('verified'))), error=r.get('error'),
                                      score=r.get('score'), longest_margin=r.get('longest_margin'), rounds=r.get('rounds'), reason=r.get('reason'),
                                      faults=r.get('faults'), caught_errors=r.get('caught_errors'), cpu_max=r.get('cpu_max'), cpu_recorded=r.get('cpu_recorded'),
                                      turns=r.get('turns'), execution_mode='server', decoder_revision=r.get('decoder_revision'), schema_version=1,
                                      replay_sha256=r.get('replay_sha256'), decoded_sha256=r.get('decoded_sha256'), experiment_id=b.get('experiment'),
                                      block_id=b.get('id'), phase=b.get('phase'), cohort=None, stages=r.get('stages'), opponent_stages=r.get('opponent_stages'),
                                      stats=r, ingested_at=db.now_iso()), 'game_id')
    manifest['counts']['results'] = origin_counts
    # --- probes and activity gates ----------------------------------------------------------------------
    probes = 0
    for cdir in sorted((live / 'state/runtime').glob('*')) if (live / 'state/runtime').exists() else []:
        if not cdir.is_dir():
            continue
        for meta in sorted(cdir.glob('*.json')):
            if meta.name == 'gate.json':
                continue
            row = read_json(meta, {})
            if 'source_fingerprint' not in row:
                continue
            probes += 1
            db.upsert(conn, 'probes', dict(id=f"{cdir.name}/{meta.stem}/{row['source_fingerprint'][:12]}", candidate_name=cdir.name, fingerprint=row['source_fingerprint'],
                                           map_id=row.get('map_id'), side=row.get('side'), toolkit_version=row.get('runner_version'), toolkit_path=None, seed=None,
                                           opponent_fingerprint=row.get('opponent_fingerprint'), map_sha256=row.get('map_sha256'), load_avg_1m=None,
                                           turns=row.get('turns'), metered=row.get('metered'), faults=row.get('faults'), caught_errors=row.get('caught_errors'),
                                           max_points=row.get('max_points'), p99_points=row.get('p99'), passed=int(bool(row.get('passed'))), error=row.get('error'),
                                           replay_path=row.get('replay'), log_sha256=row.get('log_sha256'), at=None), 'id')
    manifest['counts']['probes'] = probes
    activity = 0
    for cdir in sorted((live / 'state/activity').glob('*')) if (live / 'state/activity').exists() else []:
        gate = read_json(cdir / 'gate.json') if cdir.is_dir() else None
        if gate:
            activity += 1
            db.upsert(conn, 'contract_results', dict(id=f'legacy-activity/{cdir.name}', candidate_name=cdir.name, fingerprint=gate.get('fingerprint'),
                                                     kind='legacy_activity', reference_fingerprint=gate.get('reference_fingerprint'), detail=gate,
                                                     passed=int(bool(gate.get('passed'))), at=gate.get('at')), 'id')
    manifest['counts']['activity_gates'] = activity
    # --- events, external actions -----------------------------------------------------------------------
    executor_subs = {s['id'] for s in submissions if (s.get('name') in upload_names or re.match(r'^LV-.*-ai$', s.get('name') or ''))}
    for e in state.get('events', []):
        key = hashlib.sha256(json.dumps(e, sort_keys=True, default=str).encode()).hexdigest()[:24]
        db.upsert(conn, 'legacy_events', dict(legacy_key=key, at=e.get('at'), message=e.get('message'), payload=e), 'legacy_key')
        if e.get('message', '').startswith('Adopted externally selected incumbent'):
            db.upsert(conn, 'external_actions', dict(id='legacy/' + key, at=e.get('at'), kind='activation', submission=e.get('new'), previous=e.get('old'),
                                                     requested_by=None, note='teammate_selected' if e.get('new') in executor_subs else 'teammate_upload'), 'id')
    manifest['counts']['events'] = len(state.get('events', []))
    # --- kv snapshot ------------------------------------------------------------------------------------
    db.kv_set(conn, 'incumbent', state.get('incumbent'))
    db.kv_set(conn, 'legacy_quota_used', dict(quota=state.get('quota_used'), updated=state.get('updated')))
    db.kv_set(conn, 'map_ids', state.get('map_ids'))
    db.kv_set(conn, 'legacy_open_transactions', {k: state.get(k) for k in ('upload', 'switch', 'intent', 'probation') if state.get(k)})
    db.kv_set(conn, 'legacy_blocked_until', state.get('blocked_until'))
    db.kv_set(conn, 'legacy_excluded', state.get('excluded'))
    db.kv_set(conn, 'legacy_config', config)
    for name in ('runner_status', 'two_hour_plan', 'restoration_check', 'runner_attention'):
        db.kv_set(conn, 'legacy_' + name, read_json(live / 'state' / (name + '.json')))
    ladder = read_json(live / 'state/ladder.json', [])
    db.kv_set(conn, 'ladder', ladder)
    manifest['incumbent'] = state.get('incumbent')
    manifest['map_ids'] = state.get('map_ids')
    manifest['open_transactions'] = db.kv_get(conn, 'legacy_open_transactions')
    # --- checks -----------------------------------------------------------------------------------------
    counts = manifest['counts']
    hub = dict(candidates=conn.execute('SELECT COUNT(*) FROM candidates WHERE legacy_name IS NOT NULL').fetchone()[0],
               games=conn.execute('SELECT COUNT(*) FROM games').fetchone()[0],
               blocks=conn.execute('SELECT COUNT(*) FROM blocks').fetchone()[0],
               experiments=conn.execute("SELECT COUNT(*) FROM experiments WHERE protocol='v1'").fetchone()[0],
               requests=conn.execute('SELECT COUNT(*) FROM requests').fetchone()[0],
               legacy_events=conn.execute('SELECT COUNT(*) FROM legacy_events').fetchone()[0])
    manifest['checks']['row_counts_cover_manifest'] = (hub['candidates'] >= counts['candidates'] and hub['games'] >= sum(counts['results'].values())
                                                       and hub['blocks'] >= counts['blocks'] and hub['experiments'] >= sum(counts['experiments'].values())
                                                       and hub['requests'] >= sum(counts['requests'].values()) and hub['legacy_events'] >= counts['events'])
    manifest['hub_counts'] = hub
    try:
        # The member set is not in state.json; recompute with the requesters of our own accepted games as the executor proxy.
        own_ids = {i for r in state.get('requests', []) for i in (r.get('ids') or [])}
        requesters = {s['match'].get('requestedBy') for s in state.get('seen_series', {}).values()
                      if any(int(g['id']) in own_ids for g in s.get('games', []))}
        dev_ids = set(config.get('dev_opponents', [545, 752]))
        when = state.get('updated')
        now = time.time() if not when else __import__('datetime').datetime.fromisoformat(when.replace('Z', '+00:00')).timestamp()
        recomputed = quota_used(list(state.get('seen_series', {}).values()), state.get('requests', []), requesters, dev_ids, now)
        manifest['checks']['quota_recompute'] = dict(recomputed=recomputed, legacy=state.get('quota_used'), member_proxy=sorted(x for x in requesters if x),
                                                     note='member ids are not stored in state.json; requesters of our own accepted requests are used as the executor proxy, so teammates\' manual games are excluded here')
    except Exception as exc:  # pragma: no cover - diagnostic only
        manifest['checks']['quota_recompute'] = dict(error=repr(exc))
    db.kv_set(conn, 'last_import_manifest', manifest)
    db.event(conn, root, actor, 'legacy_import', dict(counts=counts, checks=manifest['checks']))
    return manifest
