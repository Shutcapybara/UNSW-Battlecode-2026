"""The hub executor (protocol v2): the only code that mutates the server, designed from today's incident log.

Principles (docs/hub/EXECUTOR_V2.md): one reconciling cycle at a time with no in-memory state to lose; every
mutation is a durable intent with an exact identity, reconciled against the server's own history before anything
is ever repeated; unknown fields are unknown, never losses; the control is whatever the team has live and candidates
are never orphaned by a control change; failures back off and continue, and only an unreconcilable transaction, an
identity conflict or a credential problem stops dispatch (harvest keeps running).

Modes: `shadow` (nothing is posted and no experiment, block or verdict row is written; plans are logged) and `live`.
The executor only ever evaluates, freezes or extends experiments with `protocol='v2'`; legacy v1 rows imported from
`LIVE/state` are read for evidence and frozen once, by `hubctl executor adopt-legacy`, at cutover.
"""
import gzip
import hashlib
import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import db, stats
from .api import APIError
from .contracts import evaluate as evaluate_contract

TEAM_ID_DEFAULT = 7
HARVEST_LIMIT = 60
MAX_HARVEST_ATTEMPTS = 20      # kept for the tests' fake failures; the live rule is the horizon and the backoff below (D-023)
HARVEST_HORIZON = 24 * 3600    # a game is re-fetched for a day after its request: the server's replay pipeline lags for hours under load
HARVEST_BACKOFF = 1800         # after six tries a backlog game is re-fetched every 30 min, so fresh games keep the per-cycle budget
INTENT_GRACE = 600            # seconds before a battle intent with no matching series is released
INTENT_STALE = 6 * 3600       # seconds after which an unreconciled intent pauses dispatch and pages
DEFAULT_PARAMS = dict(screen_blocks=3, confirm_blocks=6, alpha=0.025, orientations=2, max_fills=3, min_pairs=10, min_confirm_on_supersede=3, futility_fraction=0.4, pair_test=True)   # protocol v2.1 (D-019); fills per D-022
PARAMS_MIGRATIONS = ({'max_fills': 0, 'min_pairs': 14}, {'max_fills': 3, 'min_pairs': 10})   # (old values, new values) applied to running v2 experiments (D-022)
LEGACY_SHAPE_PARAMS = dict(orientations=1, max_fills=6, min_pairs=8)   # applied when the server refuses 20-map requests (kv request_shape='single')
TERMINAL = ('completed', 'failed', 'error', 'cancelled')
STAGE_ROUNDS = (25, 50, 100, 200, 250, 300, 320, 360, 380, 400, 450, 499)   # r25/r50 added 28 Sep (A1-Q1: the deficit is set before r100)
DECODER_REVISION = 'gzip-errors-v3-r25r50'                                  # the vendored decoder is unchanged; the stage set grew


CLOCK = {'now': None}   # the cycle's notion of now (tests use a synthetic clock)


def cycle_now():
    return CLOCK['now'] or time.time()


class Stop(Exception):
    """Dispatch must stop this cycle (harvest already done); the message says why."""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def ensure_columns(conn):
    have = {c[1] for c in conn.execute('PRAGMA table_info(experiments)')}
    if 'params' not in have:
        conn.execute('ALTER TABLE experiments ADD COLUMN params TEXT')
    have = {c[1] for c in conn.execute('PRAGMA table_info(games)')}
    if 'harvest_attempts' not in have:
        conn.execute('ALTER TABLE games ADD COLUMN harvest_attempts INTEGER DEFAULT 0')
    if 'harvest_at' not in have:
        conn.execute('ALTER TABLE games ADD COLUMN harvest_at REAL')   # epoch of the last fetch on the cycle's clock (backoff)
    have_b = {c[1] for c in conn.execute('PRAGMA table_info(blocks)')}
    if 'request_maps' not in have_b:
        conn.execute('ALTER TABLE blocks ADD COLUMN request_maps TEXT')
    have_c = {c[1] for c in conn.execute('PRAGMA table_info(candidates)')}
    if 'dev_only' not in have_c:
        conn.execute('ALTER TABLE candidates ADD COLUMN dev_only INTEGER DEFAULT 0')
    have = {c[1] for c in conn.execute('PRAGMA table_info(intents)')}
    if 'payload' not in have:
        conn.execute('ALTER TABLE intents ADD COLUMN payload TEXT')


def rows(conn, sql, params=()):
    return db.rows(conn, sql, params)


def loads(text, default=None):
    try:
        return json.loads(text) if text else default
    except (TypeError, ValueError):
        return default


# ----------------------------------------------------------------------------------------------- server snapshot
def budget_seconds(cfg, key, default):
    return float((cfg.get('executor') or {}).get(key, default))


class Snapshot:
    def __init__(self, client, conn, cfg, now, progress=None):
        self.client, self.conn, self.cfg, self.now = client, conn, cfg, now
        self.team_id = cfg['team']['id']
        self.history_incomplete = False
        self.progress = progress or (lambda phase, detail=None: None)
        started = time.monotonic()
        self.progress('snapshot', 'reading submissions, maps, team, ladder')
        self.subs = client.get('/api/v1/submissions')
        active = [s for s in self.subs if s.get('status') == 'active']
        if len(active) != 1:
            raise Stop(f'expected exactly one active submission, saw {len(active)}')
        self.active = active[0]['id']
        self.maps = [m for m in client.get('/api/v1/maps') if m.get('active') and not m.get('private')]
        self.map_ids = [m['id'] for m in self.maps]
        team = client.get('/api/v1/team')['team']
        if team['id'] != self.team_id:
            raise Stop('API key is for the wrong team')
        self.members = {x['id'] for x in team.get('members', [])}
        ladder_at = db.kv_get(conn, 'ladder_fetched_at') or 0
        if now - ladder_at > cfg['cadence']['cycle_seconds'] - 30:
            self.ladder = client.get('/api/v1/ratings')['ladder']
            db.kv_set(conn, 'ladder', self.ladder)
            db.kv_set(conn, 'ladder_fetched_at', now)
        else:
            self.ladder = db.kv_get(conn, 'ladder') or []
        self.dev_ids = {x['id'] for x in self.ladder if x.get('dev')}
        recent = client.get('/api/v1/battles?limit=200')
        self.history = []
        refresh_budget = 20
        deadline = started + budget_seconds(cfg, 'snapshot_seconds', 240)
        fetched = 0
        for b in recent:
            key = str(b['id'])
            if time.monotonic() > deadline:
                # the server is slow: keep what is cached, and do not pretend to know the quota this cycle
                self.history_incomplete = True
                break
            try:
                recent_enough = stats.timestamp(b['at']) > now - 7500 or b.get('outcome') == 'live'
            except Exception:
                recent_enough = True
            cached = conn.execute('SELECT payload FROM series WHERE series_id=?', (key,)).fetchone()
            payload = loads(cached['payload']) if cached else None
            stale = payload is not None and recent_enough and payload.get('match', {}).get('status') not in TERMINAL and refresh_budget > 0
            if payload is None or stale:
                if payload is None and not recent_enough:
                    continue
                payload = client.get('/api/v1/battles/' + key)
                db.upsert(conn, 'series', dict(series_id=key, payload=payload, fetched_at=now_iso()), 'series_id')
                fetched += 1
                if fetched % 10 == 0:
                    self.progress('snapshot', f'{fetched} series fetched, {round(time.monotonic() - started)} s')
                if stale:
                    refresh_budget -= 1
            if recent_enough:
                self.history.append(payload)
        for s in self.subs:
            owner = 'executor' if (s.get('name') or '').endswith('-ai') else 'teammate'
            db.upsert(conn, 'submissions', dict(id=s['id'], name=s.get('name'), source_hash=s.get('sourceHash'), language=s.get('language'),
                                                status=s.get('status'), last_seen=now_iso(), owner=owner), 'id')


# ----------------------------------------------------------------------------------------------- intents
def open_intent(conn, kind, path, payload, description):
    iid = uuid.uuid4().hex
    conn.execute('INSERT INTO intents(id,at,kind,path,body_sha256,description,status,payload) VALUES(?,?,?,?,?,?,?,?)',
                 (iid, cycle_now(), kind, path, hashlib.sha256(db.j(payload).encode()).hexdigest(), description, 'open', db.j(payload)))
    return iid


def close_intent(conn, iid, resolution, status='resolved'):
    conn.execute('UPDATE intents SET status=?, resolved_at=?, resolution=? WHERE id=?', (status, now_iso(), resolution, iid))


def open_intents(conn):
    return [dict(r, payload=loads(r['payload'], {})) for r in rows(conn, "SELECT * FROM intents WHERE status='open' ORDER BY at")]


def mutate(conn, client, kind, path, body, description, payload, content_type='application/json'):
    """Durable mutation: intent first, one POST, resolution after. 4xx resolves as rejected; 5xx/transport stays open."""
    iid = open_intent(conn, kind, path, payload, description)
    try:
        result = client.post(path, body, content_type)
    except APIError as e:
        if 400 <= e.status < 500:
            close_intent(conn, iid, f'rejected {e.status}: {e.message[:200]}', 'rejected')
            raise
        raise UncertainMutation(iid, e) from e
    close_intent(conn, iid, 'acknowledged')
    return result


class UncertainMutation(Exception):
    def __init__(self, intent_id, error):
        self.intent_id, self.error = intent_id, error
        super().__init__(f'uncertain mutation {intent_id}: {error}')


# ----------------------------------------------------------------------------------------------- transactions
def open_tx(conn, kind, payload):
    tid = uuid.uuid4().hex
    conn.execute('INSERT INTO transactions(id,kind,payload,opened_at) VALUES(?,?,?,?)', (tid, kind, db.j(payload), now_iso()))
    return tid


def close_tx(conn, tid, outcome, payload=None):
    if payload is not None:
        conn.execute('UPDATE transactions SET payload=? WHERE id=?', (db.j(payload), tid))
    conn.execute('UPDATE transactions SET closed_at=?, outcome=? WHERE id=?', (now_iso(), outcome, tid))


def open_txs(conn, kind=None):
    sql = 'SELECT * FROM transactions WHERE closed_at IS NULL' + (' AND kind=?' if kind else '')
    return [dict(r, payload=loads(r['payload'], {})) for r in rows(conn, sql, (kind,) if kind else ())]


# ----------------------------------------------------------------------------------------------- control
def control(conn):
    return db.kv_get(conn, 'control')


def set_control(conn, root, actor, submission, owner, note):
    prev = control(conn)
    db.kv_set(conn, 'control', submission)
    db.kv_set(conn, 'control_owner', owner)
    db.event(conn, root, actor, 'control_set', dict(previous=prev, control=submission, owner=owner, note=note))


def observe_control(conn, root, cfg, snap, actor, summary):
    """Own open switch → restore (unless a teammate chose something else); otherwise adopt an external change."""
    cur = control(conn)
    for tx in open_txs(conn, 'switch'):
        p = tx['payload']
        if snap.active == p['candidate']:
            summary['pending_restore'] = p
            return  # the restore is done by the dispatcher's finally or the safety loop (live mode only)
        if snap.active == p['previous']:
            close_tx(conn, tx['id'], 'restored')
        else:
            close_tx(conn, tx['id'], 'external_choice_preserved', dict(p, observed=snap.active))
    if cur is None:
        set_control(conn, root, actor, snap.active, 'unknown', 'first observation')
        return
    # An executor upload that the server auto-activated is not a teammate's choice: it is restored, never adopted
    # (28 Sep 14:26/14:51 UTC: kazuha-s01's 10357 and sakura-s01's 10376 were adopted as control; D-020). This also
    # repairs a control already poisoned that way: the restore target is the last control that was not our upload.
    active_name = next((s.get('name') or '' for s in snap.subs if s.get('id') == snap.active), '')
    fresh_upload = False
    for tx in open_txs(conn, 'upload'):
        if tx['payload'].get('name') == active_name or (active_name.endswith('-ai') and tx['payload'].get('previous') == cur and snap.active != cur):
            fresh_upload = True
    own = conn.execute("SELECT name FROM candidates WHERE submission_id=? AND status IN ('uploaded','dev_ok','dev_done','runtime_ok')", (snap.active,)).fetchone()
    if own and active_name.endswith('-ai') and snap.now - upload_seen_at(conn, snap.active) < 3 * 3600:
        fresh_upload = True
    if fresh_upload:
        previous = cur if cur != snap.active else last_non_upload_control(conn, snap)
        if previous and previous != snap.active:
            summary['pending_restore'] = dict(previous=previous, candidate=snap.active, reason='upload auto-activation' + (' (control was poisoned)' if cur == snap.active else ''))
            summary['attention'].append(dict(kind='upload_auto_activated', submission=snap.active, previous=previous))
            return
    if snap.active != cur:
        owner = next((s['owner'] for s in rows(conn, 'SELECT owner FROM submissions WHERE id=?', (snap.active,))), 'unknown')
        note = 'teammate_selected' if owner == 'executor' else 'teammate_upload'
        db.upsert(conn, 'external_actions', dict(id=f'exec/{int(snap.now)}/{snap.active}', at=now_iso(), kind='activation', submission=snap.active, previous=cur,
                                                 requested_by=None, note=note), 'id')
        summary['external_actions'].append(dict(previous=cur, submission=snap.active, note=note))
        freeze_running(conn, root, cfg, actor, cur, snap.active, summary)
        set_control(conn, root, actor, snap.active, 'teammate', note)
        db.kv_set(conn, 'probation', None)


def last_non_upload_control(conn, snap, hops=6):
    """Walk the external_actions chain back from the active submission to the last control that was not an executor upload."""
    # "our upload" means the executor's naming (`LV-…-ai`), never "a registered candidate": the teammates' control
    # 9508 is registered as the legacy candidate bifrost-v18-control and must count as a real control (15:08 UTC:
    # the walk skipped it and restored 9943 instead).
    names = {s.get('id'): (s.get('name') or '') for s in snap.subs}
    current = snap.active
    for _ in range(hops):
        row = conn.execute('SELECT previous FROM external_actions WHERE submission=? ORDER BY at DESC LIMIT 1', (current,)).fetchone()
        if not row or row['previous'] is None:
            return None
        current = row['previous']
        if not names.get(current, '').endswith('-ai'):
            return current
    return None


def upload_seen_at(conn, submission):
    """Epoch of the executor's upload event for this submission (0 when unknown)."""
    row = conn.execute("SELECT at FROM events WHERE kind='upload_reconciled' AND payload LIKE ? ORDER BY at DESC LIMIT 1", ('%"submission": ' + str(submission) + '%',)).fetchone()
    if not row:
        return 0
    try:
        return datetime.fromisoformat(row['at'].replace('Z', '+00:00')).timestamp()
    except Exception:
        return 0


def freeze_running(conn, root, cfg, actor, old, new, summary):
    """A control change freezes running comparisons; enough confirmation evidence is still evaluated (futility only)."""
    for e in rows(conn, "SELECT * FROM experiments WHERE status='running' AND protocol='v2' AND control_submission=?", (old,)):
        params = loads(e['params'], DEFAULT_PARAMS) or DEFAULT_PARAMS
        blocks, results = legacy_shapes(conn, e['id'])
        d = decide(blocks, results, params)
        complete_conf = sum(1 for x in d.get('pairs', []) if x['phase'] == 'confirm' and x['complete'])
        if d['verdict'] in ('reject_screen', 'reject_confirmation'):
            status, verdict = d['verdict'], d['verdict']
        elif complete_conf >= params['min_confirm_on_supersede']:
            status, verdict = 'superseded_incomplete', None
        else:
            status, verdict = 'superseded_by_external_activation', None
        conn.execute('UPDATE experiments SET status=?, verdict=?, decision=?, frozen_reason=?, closed_at=?, updated_at=? WHERE id=?',
                     (status, verdict, db.j({k: v for k, v in d.items() if k != 'pairs'} | {'pairs_summary': summarize_pairs(d)}), f'control changed {old}->{new}', now_iso(), now_iso(), e['id']))
        record_decision(conn, root, actor, e['id'], 'superseded', status, d, 'v2')
        summary['frozen'].append(dict(experiment=e['id'], status=status))


def decide(blocks, results, params):
    """decision_v2 with the min-pairs rule: a block that reached max_fills with >= min_pairs exact pairs counts as complete."""
    paired = stats.paired_blocks_v2(blocks, results)
    fills = {b['id']: b.get('fill_attempts', 0) for b in blocks}
    for p in paired:
        if not p['complete'] and fills.get(p['block'], 0) >= params['max_fills'] and len(p['pairs']) >= params['min_pairs']:
            ids = next((b['requests'] for b in blocks if b['id'] == p['block']), [])
            if all(results.get(str(i), {}).get('verified') or results.get(str(i), {}).get('error') for g in ids for i in g):
                p['complete'] = True
                p['accepted_by_min_pairs'] = True
    return stats.decision_v2(blocks, results, params['alpha'], params['confirm_blocks'], params['screen_blocks'], paired=paired, futility_fraction=params.get('futility_fraction'), pair_test=bool(params.get('pair_test')))


def summarize_pairs(d):
    return [dict(block=x['block'], phase=x['phase'], complete=x['complete'], delta=x['delta'], pairs=len(x['pairs']), missing=x['missing_maps'], faults=x['faults'], opponent=x['opponent']) for x in d.get('pairs', [])]


def record_decision(conn, root, actor, experiment_id, checkpoint, verdict, detail, protocol):
    conn.execute('INSERT INTO decisions(at,experiment_id,checkpoint,verdict,detail,protocol,source,created_at) VALUES(?,?,?,?,?,?,?,?)',
                 (now_iso(), experiment_id, checkpoint, verdict, db.j({k: v for k, v in detail.items() if k != 'pairs'} | {'pairs_summary': summarize_pairs(detail)}), protocol, actor, now_iso()))
    db.event(conn, root, actor, 'decision', dict(experiment=experiment_id, checkpoint=checkpoint, verdict=verdict, protocol=protocol))


# ----------------------------------------------------------------------------------------------- reconciliation
def reconcile(conn, root, cfg, snap, client, actor, summary):
    """Resolve every open intent from the server's history before deciding anything. Never re-posts."""
    for it in open_intents(conn):
        age = snap.now - it['at']
        p = it['payload']
        if it['kind'] == 'battle':
            req = conn.execute('SELECT * FROM requests WHERE id=?', (p.get('request_id'),)).fetchone()
            req = dict(req) if req else None
            match = find_series(snap, p, req)
            if match == 'ambiguous':
                summary['attention'].append(dict(kind='intent_ambiguous', intent=it['id']))
                if age > INTENT_STALE:
                    raise Stop('ambiguous battle intent older than six hours needs a human')
                continue
            if match:
                ids = [g['id'] for g in match.get('games', [])]
                known = {i for r in rows(conn, "SELECT game_ids FROM requests WHERE status='accepted'") for i in (loads(r['game_ids'], []) or [])}
                if any(i in known for i in ids):
                    conn.execute("UPDATE requests SET status='released', updated_at=? WHERE id=?", (now_iso(), p.get('request_id')))
                    close_intent(conn, it['id'], f'series already recorded {ids}', 'released')
                else:
                    conn.execute("UPDATE requests SET status='accepted', game_ids=?, updated_at=? WHERE id=?", (db.j(ids), now_iso(), p.get('request_id')))
                    attach_to_block(conn, req, ids)
                    close_intent(conn, it['id'], f'reconciled by identity: {ids}')
                    db.event(conn, root, actor, 'intent_reconciled', dict(intent=it['id'], ids=ids))
                summary['reconciled'].append(it['id'])
            elif age > INTENT_GRACE:
                conn.execute("UPDATE requests SET status='released', updated_at=? WHERE id=?", (now_iso(), p.get('request_id')))
                close_intent(conn, it['id'], 'no matching series after grace; reservation released', 'released')
                db.event(conn, root, actor, 'intent_released', dict(intent=it['id']))
                summary['reconciled'].append(it['id'])
        elif it['kind'] in ('activate', 'restore', 'promote'):
            target = p.get('submission')
            if snap.active == target:
                close_intent(conn, it['id'], 'observed active')
            elif age > INTENT_GRACE:
                close_intent(conn, it['id'], f'not active after grace (active {snap.active}); treated as not applied', 'released')
            summary['reconciled'].append(it['id'])
        elif it['kind'] == 'upload':
            name = p.get('name')
            found = [s for s in snap.subs if s.get('name') == name]
            if len(found) == 1:
                close_intent(conn, it['id'], f"upload found as {found[0]['id']}")
                summary['reconciled'].append(it['id'])
            elif len(found) > 1:
                summary['attention'].append(dict(kind='upload_ambiguous', name=name))
                raise Stop(f'upload name {name} matches {len(found)} submissions')
            elif age > INTENT_STALE:
                summary['attention'].append(dict(kind='upload_unresolved', name=name))
                raise Stop(f'upload {name} unresolved after six hours')
    finish_uploads(conn, root, cfg, snap, client, actor, summary)


def find_series(snap, payload, req):
    if not req:
        return None
    lo, hi = payload.get('at', 0) - 300, payload.get('at', 0) + 900
    matches, seen = [], set()
    for s in snap.history:
        m = s.get('match', {})
        key = m.get('seriesId') or str(m.get('id'))
        if key in seen or not m:
            continue
        seen.add(key)
        if m.get('requestedBy') not in snap.members:
            continue
        try:
            when = stats.timestamp(m['requestedAt'])
        except Exception:
            continue
        if not (lo <= when <= hi):
            continue
        if m.get('teamAId') != snap.team_id or m.get('teamBId') != req['opponent_team']:
            continue
        sid = m.get('submissionAId')
        if sid is not None and sid != req['submission']:
            continue
        if len(s.get('games', [])) != req['count']:
            continue
        if m.get('mapId') is not None and m.get('mapId') not in (loads(req['map_ids'], []) or []):
            continue
        matches.append(s)
    if len(matches) > 1:
        return 'ambiguous'
    return matches[0] if matches else None


def attach_to_block(conn, req, ids):
    if not req or not req.get('block_id'):
        return
    b = conn.execute('SELECT requests FROM blocks WHERE id=?', (req['block_id'],)).fetchone()
    if b is None:
        return
    groups = loads(b['requests'], []) or []
    groups.append(ids)
    conn.execute('UPDATE blocks SET requests=?, updated_at=? WHERE id=?', (db.j(groups), now_iso(), req['block_id']))


def finish_uploads(conn, root, cfg, snap, client, actor, summary):
    """Exact-name reconciliation of open upload transactions; undo an auto-activation; preserve teammate choices."""
    for tx in open_txs(conn, 'upload'):
        p = tx['payload']
        found = [s for s in snap.subs if s.get('name') in (p['name'],)]
        if len(found) != 1:
            if snap.now - stats.timestamp(tx['opened_at']) > INTENT_STALE:
                raise Stop(f"upload {p['name']} not found after six hours; never re-uploaded")
            continue
        sub = found[0]
        conn.execute("UPDATE candidates SET submission_id=?, upload_name=?, api_source_hash=?, status=CASE WHEN status IN ('runtime_ok','uploaded') THEN 'uploaded' ELSE status END, updated_at=? WHERE fingerprint=?",
                     (sub['id'], sub['name'], sub.get('sourceHash'), now_iso(), p['fingerprint']))
        if snap.active == sub['id']:
            if control(conn) == sub['id']:
                pass  # a teammate chose it; the control observer already adopted it
            else:
                summary['pending_restore'] = dict(previous=p['previous'], candidate=sub['id'], reason='upload auto-activation')
                if summary.get('mode') == 'live':
                    restore(conn, root, cfg, snap, client, actor, p['previous'], sub['id'], 'undo upload auto-activation')
        close_tx(conn, tx['id'], f"uploaded as {sub['id']}")
        db.event(conn, root, actor, 'upload_reconciled', dict(name=p['name'], submission=sub['id'], build=sub.get('status')))
        summary['uploads'].append(dict(name=p['name'], submission=sub['id']))


def restore(conn, root, cfg, snap, client, actor, previous, candidate, reason):
    """Re-activate `previous` only if `candidate` is what is active now (never overwrite a teammate's choice)."""
    active = [s for s in client.get('/api/v1/submissions') if s.get('status') == 'active']
    active = active[0]['id'] if len(active) == 1 else None
    if active != candidate:
        db.event(conn, root, actor, 'restore_skipped', dict(previous=previous, candidate=candidate, active=active, reason=reason))
        return False
    mutate(conn, client, 'restore', f'/api/v1/submissions/{previous}/activate', {}, reason, dict(submission=previous, candidate=candidate))
    db.event(conn, root, actor, 'restored', dict(previous=previous, candidate=candidate, reason=reason))
    return True


# ----------------------------------------------------------------------------------------------- harvest
def runtime_exceptions(decoded_path, side):
    from .vendor.public_replay_review import Reader
    reader = Reader(decoded_path)
    root = reader.object(0, 0)
    teams, actor, round_number, events = {}, None, -1, set()
    for line in root.text(0).splitlines():
        bits = line.split()
        if bits and bits[0] == 'DRAGON':
            teams[len(teams)] = 'AB'[int(bits[1])]
    for event in root.items(3):
        kind = event.num(0, 'H')
        obj = event.child(0)
        if kind == 0:
            round_number = obj.num()
        elif kind == 1:
            actor = obj.num()
        elif kind == 10:
            teams[obj.num(4)] = teams[obj.num()]
        elif kind in (5, 6) and teams.get(actor) == side:
            text = obj.text(0)
            if 'MC_ERROR ' in text:
                events.add((round_number, actor, text.strip()))
    return sorted(events)


def analyse_replay(decoded_path):
    from .vendor.public_replay_review import analyse
    return analyse(decoded_path)


def harvest(conn, root, cfg, snap, client, actor, summary, limit=HARVEST_LIMIT):
    """Verify pending games within a time budget: running v2 blocks first, then dev coverage, then the backlog."""
    running = {b['id'] for b in rows(conn, "SELECT b.id FROM blocks b JOIN experiments e ON e.id=b.experiment_id WHERE e.status='running' AND e.protocol='v2'")}
    pending = []
    now = cycle_now()
    for r in rows(conn, "SELECT * FROM requests WHERE status='accepted' ORDER BY at"):
        if (r['at'] or now) < now - HARVEST_HORIZON:
            continue
        for gid in loads(r['game_ids'], []) or []:
            g = conn.execute('SELECT verified, harvest_attempts, error, harvest_at FROM games WHERE game_id=?', (gid,)).fetchone()
            rank = 0 if r['block_id'] in running else 1 if r['pool'] == 'dev' else 2
            if g is not None:
                if g['verified'] or g['error'] == 'server infrastructure failure':
                    continue
                attempts = g['harvest_attempts'] or 0
                incomplete = (g['error'] or '').startswith(('incomplete API payload', 'replay not yet available'))
                if attempts >= MAX_HARVEST_ATTEMPTS and not incomplete:
                    continue   # a decode/download failure that repeats is not going to change
                if rank and attempts >= 6 and now - (g['harvest_at'] or 0) < HARVEST_BACKOFF:
                    continue   # backlog backoff; running blocks are always re-fetched
            pending.append((rank, gid, r))
    pending.sort(key=lambda x: (x[0], x[1]))
    deadline = time.monotonic() + budget_seconds(cfg, 'harvest_seconds', 240)
    done = 0
    for rank, gid, req in pending[:limit]:
        if done and time.monotonic() > deadline:
            break
        done += 1
        if done % 5 == 0:
            snap.progress('harvest', f'{done}/{len(pending)} games')
        try:
            harvest_one(conn, root, cfg, snap, client, gid, req)
        except Exception as exc:
            prior = conn.execute('SELECT harvest_attempts FROM games WHERE game_id=?', (gid,)).fetchone()
            attempts = ((prior['harvest_attempts'] if prior else 0) or 0) + 1
            db.upsert(conn, 'games', dict(game_id=gid, own_submission=req['submission'], opponent_team=req['opponent_team'], pool=req['pool'], origin=req['origin'] or 'controlled',
                                          verified=0, status='unverified', error='harvest error: ' + type(exc).__name__ + ': ' + str(exc)[:200], harvest_attempts=attempts, harvest_at=cycle_now(),
                                          block_id=req['block_id'], ingested_at=now_iso()), 'game_id')
            summary['harvest_errors'].append(dict(game_id=gid, error=str(exc)[:120]))
    summary['harvest'] = dict(pending=len(pending), attempted=done, backlog=max(0, len(pending) - done))
    summary['candidate_games'] = candidate_games(conn)
    summary['incomplete_payload_sample'] = db.kv_get(conn, 'incomplete_payload_sample')


def candidate_games(conn):
    """Per registered candidate with a submission: requested / verified / unverified games by pool and the unverified
    error kinds, so a candidate stuck at 'uploaded' can be read from the mirror without opening the database."""
    out = {}
    for c in rows(conn, "SELECT name, submission_id, status FROM candidates WHERE submission_id IS NOT NULL AND status IN ('uploaded','dev_ok','dev_done','runtime_ok')"):
        sid = c['submission_id']
        requested = {}
        for r in rows(conn, "SELECT pool, game_ids, status FROM requests WHERE submission=? AND status IN ('reserved','accepted')", (sid,)):
            requested[r['pool']] = requested.get(r['pool'], 0) + len(loads(r['game_ids'], []) or [])
        games = rows(conn, "SELECT pool, verified, error, harvest_attempts FROM games WHERE own_submission=?", (sid,))
        verified = {}
        errors = {}
        for g in games:
            if g['verified']:
                verified[g['pool']] = verified.get(g['pool'], 0) + 1
            else:
                key = (g['error'] or 'pending')[:60]
                errors[key] = errors.get(key, 0) + 1
        out[c['name']] = dict(submission=sid, status=c['status'], requested=requested, verified=verified, unverified=errors)
    return out


def harvest_one(conn, root, cfg, snap, client, gid, req):
    payload = client.get(f'/api/v1/battles/{gid}')
    m = payload.get('match', {})
    if m.get('status') not in TERMINAL:
        return
    side = 'A' if m.get('teamAId') == snap.team_id else 'B'
    other = 'B' if side == 'A' else 'A'
    listed = next((g for g in (payload.get('games') or []) if isinstance(g, dict) and g.get('id') == gid), {})
    reported = m.get('submission' + side + 'Id')
    row = dict(game_id=gid, submission=reported if reported is not None else req['submission'], side=side, map_id=m.get('mapId'), map_name=payload.get('mapName'), series=m.get('seriesId'),
               requested=m.get('requestedAt'), seed=m.get('seed'), pool=req['pool'], verified=False, origin=req['origin'] or 'controlled',
               opponent=m.get('team' + other + 'Id'), opponent_submission=m.get('submission' + other + 'Id'), faults=None,
               attribution='api' if reported is not None else 'request')   # D-023: since 28 Sep the payload carries no submission ids; the request's activation attributes the game
    prior = conn.execute('SELECT harvest_attempts FROM games WHERE game_id=?', (gid,)).fetchone()
    attempts = ((prior['harvest_attempts'] if prior else 0) or 0) + 1
    has_replay = bool(m.get('replayKey')) or bool(listed.get('hasReplay')) or ('replayKey' not in m and 'hasReplay' not in listed)   # unknown shape: try the download
    if reported is None and not getattr(snap, 'incomplete_sample_logged', False):   # one raw sample per cycle, so the server's payload shape is on record
        snap.incomplete_sample_logged = True
        db.kv_set(conn, 'incomplete_payload_sample', dict(game_id=gid, payload=payload))
    if m.get('status') != 'completed':
        row['error'] = 'server infrastructure failure'
    elif not has_replay:
        row['error'] = 'replay not yet available'   # transient: re-fetched under the harvest horizon
    else:
        raw_dir = Path(root) / 'replays' / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)
        replay = raw_dir / f'{gid}.replay'
        if not replay.exists():
            client.download_replay(gid, replay)
        raw = replay.read_bytes()
        packed = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
        decoded = Path(root) / 'replays' / 'decoded' / f'{gid}.replay'
        decoded.parent.mkdir(parents=True, exist_ok=True)
        if not decoded.exists() or decoded.read_bytes() != packed:
            decoded.write_bytes(packed)
        try:
            a = analyse_replay(decoded)
            expected = (m.get('winner') or 'draw')
            if a['winner'].lower() != expected.lower():
                raise ValueError('API/replay winner mismatch')
            st = a['stats'][side]
            final, curve = a['final'], a['curve']
            exceptions = runtime_exceptions(decoded, side)
            pick = lambda t, r: next((x[t] for x in curve if x['round'] == r), curve[-1][t])
            stages = {str(r): pick(side, r) for r in STAGE_ROUNDS}
            other_stages = {str(r): pick(other, r) for r in STAGE_ROUNDS}
            row.update(verified=True, score=.5 if a['winner'] == 'draw' else float(a['winner'] == side), longest_margin=final[side]['longest'] - final[other]['longest'],
                       final=final[side], rounds=a['rounds'], reason=a['reason'], faults=st.get('tle', 0), turns=st.get('turns', 0), caught_errors=len(exceptions),
                       exception_examples=exceptions[:10], cpu_max=st.get('cpu_max'), cpu_recorded=st.get('cpu_recorded', 0), map_hash=a['map_hash'],
                       replay_sha256=hashlib.sha256(raw).hexdigest(), decoded_sha256=hashlib.sha256(packed).hexdigest(), stages=stages, opponent_stages=other_stages,
                       early_elimination=a['rounds'] < 320 and final[side]['units'] == 0, stats=st)
            if reported is not None and reported != req['submission']:
                row['verified'] = False
                row['error'] = 'submission mismatch: excluded from inference'
        except Exception as exc:
            row['error'] = type(exc).__name__ + ': ' + str(exc)[:200]
    row['decoder_revision'] = DECODER_REVISION
    db.upsert(conn, 'games', dict(game_id=gid, series_id=row.get('series'), requested_at=row.get('requested'), ranked=int(bool(m.get('ranked'))), pool=row['pool'], origin=row['origin'],
                                  own_submission=row['submission'], opponent_team=row['opponent'], opponent_submission=row.get('opponent_submission'), map_id=row['map_id'], map_name=row['map_name'],
                                  map_hash=row.get('map_hash'), api_side=side, observed_side=side, seed=row.get('seed'), status='verified' if row['verified'] else 'unverified',
                                  verified=int(bool(row['verified'])), error=row.get('error'), score=row.get('score'), longest_margin=row.get('longest_margin'), rounds=row.get('rounds'),
                                  reason=row.get('reason'), faults=row.get('faults'), caught_errors=row.get('caught_errors'), cpu_max=row.get('cpu_max'), cpu_recorded=row.get('cpu_recorded'),
                                  turns=row.get('turns'), execution_mode='server', decoder_revision=DECODER_REVISION, schema_version=3, replay_sha256=row.get('replay_sha256'),
                                  decoded_sha256=row.get('decoded_sha256'), block_id=req['block_id'], stages=row.get('stages'), opponent_stages=row.get('opponent_stages'), stats=row,
                                  harvest_attempts=attempts, harvest_at=cycle_now(), ingested_at=now_iso()), 'game_id')


# ----------------------------------------------------------------------------------------------- ledger views
def legacy_shapes(conn, experiment_id=None):
    blocks = []
    sql = 'SELECT * FROM blocks' + (' WHERE experiment_id=?' if experiment_id else '')
    for b in rows(conn, sql, (experiment_id,) if experiment_id else ()):
        if b['excluded_reason']:
            continue
        blocks.append(dict(id=b['id'], phase=b['phase'], control=b['control_submission'], candidate=b['candidate_submission'], opponent=b['opponent_team'],
                           map_ids=loads(b['map_ids'], []) or [], request_maps=loads(b.get('request_maps'), []) or None, experiment=b['experiment_id'],
                           requests=loads(b['requests'], []) or [], fill_attempts=b['fill_attempts'] or 0, order=loads(b.get('order_json'), None)))
    results = {}
    for g in rows(conn, 'SELECT game_id, stats FROM games'):
        r = loads(g['stats'])
        if isinstance(r, dict):
            results[str(g['game_id'])] = r
    return blocks, results


def quota(conn, cfg, snap):
    reservations = [dict(at=r['at'], status=r['status'], pool=r['pool'], ids=loads(r['game_ids'], []) or [], count=r['count'])
                    for r in rows(conn, "SELECT at,status,pool,game_ids,count FROM requests WHERE status IN ('reserved','accepted')")]
    used = stats.quota_used(snap.history, reservations, snap.members, snap.dev_ids, snap.now)
    out = {}
    for pool in ('field', 'dev'):
        blocked = conn.execute('SELECT until FROM quota_blocks WHERE pool=?', (pool,)).fetchone()
        blocked_until = blocked['until'] if blocked else 0
        cap = min(cfg['budget']['hourly_games'][pool] - used[pool], cfg['budget']['executor_cap'][pool] - executor_used(conn, pool, snap.now))
        available = max(0, cap) if snap.now > blocked_until else 0
        if getattr(snap, 'history_incomplete', False):
            available = 0   # a slow server cut the history short: never request on an unknown quota picture
        out[pool] = dict(used=used[pool], available=available, blocked_until=blocked_until, unknown=bool(getattr(snap, 'history_incomplete', False)))
    return out


def executor_used(conn, pool, now):
    return sum(r['count'] or 0 for r in rows(conn, "SELECT count FROM requests WHERE pool=? AND at>? AND status IN ('reserved','accepted')", (pool, now - 3605)))


# ----------------------------------------------------------------------------------------------- planning helpers
def dev_pass(conn, cfg, snap, submission):
    covered = {(r['opponent_team'], r['map_id']) for r in rows(conn, "SELECT opponent_team, map_id FROM games WHERE pool='dev' AND verified=1 AND own_submission=?", (submission,))}
    required = {(d, m) for d in cfg['team']['dev_opponents'] for m in snap.map_ids}
    if not required <= covered:
        return False
    bad = rows(conn, "SELECT faults, caught_errors, cpu_max, cpu_recorded, turns FROM games WHERE pool='dev' AND verified=1 AND own_submission=?", (submission,))
    return not any((g['faults'] or 0) or (g['caught_errors'] or 0) or (g['cpu_recorded'] != g['turns']) or ((g['cpu_max'] or 10**9) >= cfg['runtime']['live_gate']['max_points']) for g in bad)


def dev_missing(conn, cfg, snap, submission):
    scheduled = {(r['opponent_team'], m) for r in rows(conn, "SELECT opponent_team, map_ids FROM requests WHERE pool='dev' AND submission=? AND status IN ('reserved','accepted')", (submission,)) for m in (loads(r['map_ids'], []) or [])}
    covered = {(r['opponent_team'], r['map_id']) for r in rows(conn, "SELECT opponent_team, map_id FROM games WHERE pool='dev' AND verified=1 AND own_submission=?", (submission,))}
    out = {}
    for d in cfg['team']['dev_opponents']:
        missing = [m for m in snap.map_ids if (d, m) not in covered and (d, m) not in scheduled]
        if missing:
            out[d] = missing
    return out


def in_blackout(cfg, now):
    minute = int((now % 86400) // 60)
    g = cfg['ranked_exposure_guard']
    return stats.in_blackout(minute, g['blackout_before_even_utc_hour_minutes'], g['blackout_after_even_utc_hour_minutes'])


def ranked_recent(snap, limit=12):
    """Our ranked series in the server's recent history, newest first: what the rating is being decided on."""
    out = []
    for payload in getattr(snap, 'history', []) or []:
        m = payload.get('match') or {}
        if not m.get('ranked') or snap.team_id not in (m.get('teamAId'), m.get('teamBId')):
            continue
        side = 'A' if m.get('teamAId') == snap.team_id else 'B'
        games = payload.get('games') or []
        wins = sum(1 for g in games if (g.get('winner') or '').lower() == side.lower())
        losses = sum(1 for g in games if (g.get('winner') or '').lower() == ('b' if side == 'A' else 'a'))
        out.append(dict(series=m.get('seriesId') or m.get('id'), at=m.get('requestedAt'), started=m.get('startedAt'), requested_by=m.get('requestedBy'),
                        opponent=m.get('teamBId') if side == 'A' else m.get('teamAId'), side=side, our_submission=m.get('submission' + side + 'Id'),
                        status=m.get('status'), games=len(games), wins=wins, losses=losses, elo=m.get('eloChange' + side) if m.get('eloChange' + side) is not None else m.get('eloChangeA' if side == 'A' else 'eloChangeB')))
    out.sort(key=lambda r: r.get('at') or '', reverse=True)
    return out[:limit]


def ranked_in_flight(snap):
    """A ranked series involving us that is not terminal (autoscrims start 4–36 min after the even hour, and other
    teams challenge at arbitrary times — A1-Q9): a candidate must not be active while one could bind."""
    for payload in getattr(snap, 'history', []) or []:
        m = payload.get('match') or {}
        if m.get('ranked') and snap.team_id in (m.get('teamAId'), m.get('teamBId')) and m.get('status') not in TERMINAL:
            return m.get('id') or m.get('seriesId')
    return None


def reserve(conn, pool, opponent, submission, map_ids, block_id, origin='controlled'):
    rid = uuid.uuid4().hex
    db.upsert(conn, 'requests', dict(id=rid, at=cycle_now(), pool=pool, opponent_team=opponent, submission=submission, map_ids=map_ids, count=len(map_ids), status='reserved', game_ids=[], block_id=block_id, origin=origin), 'id')
    return rid


def waves_of_distinct_maps(maps):
    """One server request creates at most one game per distinct map (D-022: a 20-entry request came back as 10 games).
    Split a request list into consecutive waves with no repeated map, preserving order, so the two halves of the
    rotation pattern (M0..M9 then M1..M9,M0) stay whole and consecutive ids keep their parity relationship."""
    waves, cur, seen = [], [], set()
    for m in maps:
        if m in seen:
            waves.append(cur)
            cur, seen = [], set()
        cur.append(m)
        seen.add(m)
    if cur:
        waves.append(cur)
    return waves


def aligned(wave, k, map_ids):
    """The k-th arm's order for a fill wave. Arms post back to back, so the second arm's ids sit len(wave) after the
    first's: an even wave keeps its order (same parity per position); an odd wave gets a spare block map in front, which
    shifts every position by one (the spare game is a harmless extra); with no spare map left, rotate by one (every
    map but the wrapped one aligns, and the next fill finishes it)."""
    wave = list(wave)
    if k == 0 or len(wave) % 2 == 0:
        return wave
    spare = next((m for m in map_ids if m not in wave), None)
    return [spare] + wave if spare is not None else wave[1:] + wave[:1]


def spread(maps):
    """[m1, m1, m2] -> [m1, m2, m1]: first occurrences of every map, then second ones, so fills split into few waves."""
    order = list(dict.fromkeys(maps))
    counts = {m: maps.count(m) for m in order}
    return [m for k in range(max(counts.values(), default=0)) for m in order if counts[m] > k]


def request_batch(conn, root, cfg, snap, client, actor, submission, opponent, map_ids, pool, block_id, summary, waves=None):
    """Reserve, (switch), POST, attach, restore. Returns game ids or None. Raises Stop on a lost acknowledgement.

    `waves`: further map lists posted back to back inside the same activation, each its own request row (D-022:
    a block arm is two waves of the block's distinct maps, the second rotated by one, so that consecutive ids give
    every map both starting layouts)."""
    if pool == 'field' and opponent in snap.dev_ids:
        pool = 'dev'
    active = snap.active
    if submission != active and in_blackout(cfg, snap.now):
        summary['deferred'].append(dict(reason='ranked_exposure_blackout', submission=submission, opponent=opponent))
        return None
    if submission != active and ranked_in_flight(snap):
        summary['deferred'].append(dict(reason='ranked_series_in_flight', series=ranked_in_flight(snap), submission=submission, opponent=opponent))
        return None
    all_waves = [list(map_ids)] + [list(w) for w in (waves or []) if w]
    rid = None
    all_ids = []
    switched = None
    try:
        if submission != active:
            switched = open_tx(conn, 'switch', dict(previous=active, candidate=submission))
            mutate(conn, client, 'activate', f'/api/v1/submissions/{submission}/activate', {}, 'temporary activation for a test batch', dict(submission=submission, previous=active))
        for wave in all_waves:
            rid = reserve(conn, pool, opponent, submission, wave, block_id)
            out = mutate(conn, client, 'battle', '/api/v1/battles', dict(teamId=opponent, ranked=False, mapIds=wave), f'request unranked games block {block_id}',
                         dict(at=snap.now, request_id=rid, submission=submission, opponent=opponent, map_ids=wave))
            ids = out.get('ids') or []
            conn.execute("UPDATE requests SET status='accepted', game_ids=?, count=?, updated_at=? WHERE id=?", (db.j(ids), len(ids), now_iso(), rid))
            if block_id:
                attach_to_block(conn, dict(block_id=block_id), ids)
            if len(ids) != len(wave):
                summary['attention'].append(dict(kind='unexpected_game_count', ids=ids, requested=len(wave)))
            db.event(conn, root, actor, 'batch_requested', dict(submission=submission, opponent=opponent, maps=len(wave), ids=ids, pool=pool, block=block_id))
            summary['dispatched'].append(dict(submission=submission, opponent=opponent, maps=len(wave), ids=ids, pool=pool))
            all_ids.extend(ids)
        return all_ids
    except APIError as e:
        if 400 <= e.status < 500:
            conn.execute("UPDATE requests SET status='rejected', updated_at=? WHERE id=?", (now_iso(), rid))
            if e.status == 429:
                until = snap.now + (e.retry_after or 3605)
                conn.execute('INSERT OR REPLACE INTO quota_blocks(pool,until,reason) VALUES(?,?,?)', (pool, until, e.message[:200]))
                summary['attention'].append(dict(kind='quota_rejection', pool=pool, until=until))
            elif e.status == 400 and len(map_ids) > len(snap.map_ids) and db.kv_get(conn, 'request_shape') != 'single':
                # the two-orientation 20-map request is not accepted: fall back to single-orientation blocks with fills (A1-Q3 fallback)
                db.kv_set(conn, 'request_shape', 'single')
                summary['request_shape_refused'] = True
                summary['attention'].append(dict(kind='request_shape_unsupported', message=e.message[:200]))
                db.event(conn, root, actor, 'request_shape_unsupported', dict(message=e.message[:200], maps=len(map_ids)))
            elif e.status in (400, 403, 404):
                conn.execute('INSERT OR REPLACE INTO opponent_exclusions(team_id,until,reason) VALUES(?,?,?)', (opponent, snap.now + 3600, e.message[:200]))
            db.event(conn, root, actor, 'batch_rejected', dict(status=e.status, opponent=opponent, pool=pool, message=e.message[:200]))
            return all_ids or None
        raise
    except UncertainMutation as e:
        db.event(conn, root, actor, 'mutation_uncertain', dict(intent=e.intent_id, error=str(e.error)[:200]))
        raise Stop(f'uncertain mutation {e.intent_id}; reconciled next cycle')
    finally:
        if switched:
            try:
                restore(conn, root, cfg, snap, client, actor, active, submission, 'restore after test batch')
                close_tx(conn, switched, 'restored')
            except (APIError, UncertainMutation) as e:
                db.event(conn, root, actor, 'restore_uncertain', dict(error=str(e)[:200]))
                summary['attention'].append(dict(kind='restore_uncertain', candidate=submission, previous=active))


# ----------------------------------------------------------------------------------------------- experiments
def screen_panel(cfg, conn, snap):
    return list(cfg['panels']['screen'])


def confirmation_panel(cfg, conn, snap, screen):
    return [o for o in cfg['panels']['confirmation'] if o not in screen]


def open_experiment(conn, root, cfg, snap, actor, cand, summary):
    ctrl = control(conn)
    tried = conn.execute("SELECT 1 FROM experiments WHERE control_submission=? AND candidate_name=? AND status NOT IN ('superseded_by_external_activation','superseded_incomplete','superseded_by_cutover')", (ctrl, cand['name'])).fetchone()
    if tried:
        return None
    week_ago = datetime.fromtimestamp(snap.now - 7 * 86400, timezone.utc).isoformat()
    lineage_losses = conn.execute("SELECT COUNT(*) FROM experiments e JOIN candidates c ON c.name=e.candidate_name WHERE c.lineage=? AND e.verdict LIKE 'reject%' AND e.closed_at > ?",
                                  (cand['lineage'], week_ago)).fetchone()[0]
    if lineage_losses >= 2 and not conn.execute("SELECT 1 FROM findings WHERE kind IN ('design','hypothesis') AND body LIKE ?", ('%' + cand['name'] + '%',)).fetchone():
        summary['deferred'].append(dict(reason='lineage_needs_finding', candidate=cand['name']))
        return None
    screen = screen_panel(cfg, conn, snap)
    eid = uuid.uuid4().hex
    params = dict(DEFAULT_PARAMS)
    db.upsert(conn, 'experiments', dict(id=eid, candidate_name=cand['name'], candidate_submission=cand['submission_id'], control_submission=ctrl, protocol='v2', protocol_label='v2.1' if params.get('pair_test') else 'v2', alpha=params['alpha'],
                                        screen_opponents=screen, confirmation_opponents=confirmation_panel(cfg, conn, snap, screen), map_ids=snap.map_ids, status='running',
                                        params=params, source_fingerprint=cand['fingerprint'], opened_at=now_iso()), 'id')
    db.event(conn, root, actor, 'experiment_opened', dict(id=eid, candidate=cand['name'], submission=cand['submission_id'], control=ctrl, screen=screen))
    summary['opened'].append(eid)
    return dict(rows(conn, 'SELECT * FROM experiments WHERE id=?', (eid,))[0])


def request_shape(conn, params):
    """'double' (each map on both starting orientations: the waves M0..M9 and M1..M9,M0 posted back to back — A1-Q3, D-022)
    unless the server refused it."""
    if params.get('orientations', 1) == 2 and db.kv_get(conn, 'request_shape') != 'single':
        return 'double'
    return 'single'


def effective_params(conn, params):
    return dict(params, **LEGACY_SHAPE_PARAMS) if request_shape(conn, params) == 'single' and params.get('orientations', 1) == 2 else params


def rotation(maps):
    """Each map twice so that its two positions have opposite parity (game ids in one request are consecutive, and the
    starting orientation is f(map, id parity) — A1-Q3): rotate by one for an even count, repeat in place for an odd one."""
    maps = list(maps)
    return maps + (maps[1:] + maps[:1] if len(maps) % 2 == 0 else maps)


def new_block(conn, e, phase, opponent, params=None):
    bid = uuid.uuid4().hex
    order = [e['control_submission'], e['candidate_submission']]
    random.Random(bid).shuffle(order)
    maps = loads(e['map_ids'], [])
    req = rotation(maps) if request_shape(conn, params or DEFAULT_PARAMS) == 'double' else list(maps)
    db.upsert(conn, 'blocks', dict(id=bid, experiment_id=e['id'], phase=phase, control_submission=e['control_submission'], candidate_submission=e['candidate_submission'],
                                   opponent_team=opponent, map_ids=maps, request_maps=req, order_json=order, requests=[], fill_attempts=0), 'id')
    return dict(id=bid, order=order, map_ids=maps, request_maps=req, opponent=opponent, phase=phase)


def evaluate(conn, root, cfg, snap, client, actor, summary):
    """Decision checkpoints for the executor's own (protocol v2) running experiments; legacy v1 rows are never touched."""
    for e in rows(conn, "SELECT * FROM experiments WHERE status='running' AND protocol='v2'"):
        params = loads(e['params'], DEFAULT_PARAMS) or DEFAULT_PARAMS
        blocks, results = legacy_shapes(conn, e['id'])
        d = decide(blocks, results, params)
        conn.execute('UPDATE experiments SET decision=?, updated_at=? WHERE id=?', (db.j({k: v for k, v in d.items() if k != 'pairs'} | {'pairs_summary': summarize_pairs(d)}), now_iso(), e['id']))
        tested = {i for b in blocks for g in b['requests'] for i in g}
        bad = [i for i in tested if results.get(str(i), {}).get('verified') and results[str(i)]['submission'] == e['candidate_submission'] and (results[str(i)].get('faults') or results[str(i)].get('caught_errors'))]
        if bad:
            d = dict(d, verdict='runtime_invalid', bad=bad[:10])
        if d['verdict'] in ('reject_screen', 'reject_confirmation', 'runtime_invalid'):
            conn.execute('UPDATE experiments SET status=?, verdict=?, closed_at=?, updated_at=? WHERE id=?', (d['verdict'], d['verdict'], now_iso(), now_iso(), e['id']))
            record_decision(conn, root, actor, e['id'], 'checkpoint', d['verdict'], d, 'v2')
            conn.execute("UPDATE candidates SET status='retired', retired_reason=?, updated_at=? WHERE name=?", ('strategy_lost_' + d['verdict'].split('_')[-1] if d['verdict'] != 'runtime_invalid' else 'runtime_invalid', now_iso(), e['candidate_name']))
            summary['verdicts'].append(dict(experiment=e['id'], verdict=d['verdict']))
        elif d['verdict'] == 'promote':
            record_decision(conn, root, actor, e['id'], 'checkpoint', 'promote', d, 'v2')
            if summary['mode'] != 'live':
                summary['verdicts'].append(dict(experiment=e['id'], verdict='promote (shadow: not applied)'))
                conn.execute("UPDATE experiments SET status='promote', verdict='promote', closed_at=?, updated_at=? WHERE id=?", (now_iso(), now_iso(), e['id']))
                continue
            if snap.active != e['control_submission']:
                summary['attention'].append(dict(kind='promotion_blocked', reason='control changed before promotion'))
                continue
            tid = open_tx(conn, 'promotion', dict(candidate=e['candidate_submission'], previous=e['control_submission'], experiment=e['id']))
            try:
                mutate(conn, client, 'promote', f"/api/v1/submissions/{e['candidate_submission']}/activate", {}, 'promote after fresh live confirmation', dict(submission=e['candidate_submission']))
            except UncertainMutation:
                summary['attention'].append(dict(kind='promotion_uncertain', experiment=e['id']))
                raise Stop('promotion acknowledgement lost; reconciled next cycle')
            close_tx(conn, tid, 'activated')
            set_control(conn, root, actor, e['candidate_submission'], 'executor', f"promoted from experiment {e['id']}")
            db.kv_set(conn, 'probation', dict(candidate=e['candidate_submission'], previous=e['control_submission'], started=snap.now, experiment=e['id']))
            conn.execute("UPDATE experiments SET status='promote', verdict='promote', closed_at=?, updated_at=? WHERE id=?", (now_iso(), now_iso(), e['id']))
            conn.execute("UPDATE candidates SET status='promoted', updated_at=? WHERE name=?", (now_iso(), e['candidate_name']))
            summary['verdicts'].append(dict(experiment=e['id'], verdict='promote'))


def monitor_probation(conn, root, cfg, snap, client, actor, summary):
    p = db.kv_get(conn, 'probation')
    if not p:
        return
    if control(conn) != p['candidate']:
        db.kv_set(conn, 'probation', None)
        return
    bad = rows(conn, "SELECT game_id FROM games WHERE verified=1 AND own_submission=? AND requested_at>? AND (faults>0 OR caught_errors>0)",
               (p['candidate'], datetime.fromtimestamp(p['started'], timezone.utc).isoformat()))
    if bad and summary['mode'] == 'live' and snap.active == p['candidate']:
        mutate(conn, client, 'restore', f"/api/v1/submissions/{p['previous']}/activate", {}, 'automatic rollback after runtime fault during probation', dict(submission=p['previous']))
        set_control(conn, root, actor, p['previous'], 'executor', 'probation rollback')
        db.kv_set(conn, 'probation', None)
        summary['verdicts'].append(dict(experiment=p['experiment'], verdict='probation_rollback', games=[b['game_id'] for b in bad][:10]))


def plan_and_dispatch(conn, root, cfg, snap, client, actor, q, summary):
    live = summary['mode'] == 'live'
    ctrl = control(conn)
    # 1. uploads: one per cycle
    for c in rows(conn, "SELECT * FROM candidates WHERE status='runtime_ok' AND submission_id IS NULL ORDER BY priority DESC LIMIT 1"):
        summary['plan'].append(dict(action='upload', candidate=c['name']))
        if live and not open_txs(conn, 'upload'):
            upload(conn, root, cfg, snap, client, actor, c, summary)
    # 2. dev coverage: control first, then uploaded candidates
    targets = [ctrl] + [c['submission_id'] for c in rows(conn, "SELECT submission_id FROM candidates WHERE status IN ('uploaded','dev_ok') AND submission_id IS NOT NULL ORDER BY priority DESC")]
    for sid in targets:
        if sid is None:
            continue
        for opp, maps in dev_missing(conn, cfg, snap, sid).items():
            take = maps[:q['dev']['available']]
            if not take:
                break
            summary['plan'].append(dict(action='dev', submission=sid, opponent=opp, maps=len(take)))
            if live:
                ids = request_batch(conn, root, cfg, snap, client, actor, sid, opp, take, 'dev', None, summary)
                if ids:
                    q['dev']['available'] -= len(take)
    for c in rows(conn, "SELECT name, submission_id, dev_only FROM candidates WHERE status='uploaded' AND submission_id IS NOT NULL"):
        if dev_pass(conn, cfg, snap, c['submission_id']):
            status = 'dev_done' if c['dev_only'] else 'dev_ok'   # dev_only: a diagnostic upload (e.g. the A1-Q8 stdin tap) is never screened
            conn.execute("UPDATE candidates SET status=?, updated_at=? WHERE name=?", (status, now_iso(), c['name']))
            if status == 'dev_done':
                db.event(conn, root, actor, 'dev_only_done', dict(candidate=c['name'], submission=c['submission_id']))
    # 3. the running experiment (or open one)
    # any running experiment whose control is no longer the control is frozen, however the control changed
    # (28 Sep 15:13 UTC: a director restore left yuna-v03 vs 10376 'running' with control 9508, then 10413 — nothing
    # was dispatched for an hour because the next-block rule waits for active == the experiment's control)
    for stale in rows(conn, "SELECT * FROM experiments WHERE status='running' AND protocol='v2' AND control_submission != ?", (ctrl,)):
        freeze_running(conn, root, cfg, actor, stale['control_submission'], ctrl, summary)
    running = rows(conn, "SELECT * FROM experiments WHERE status='running' AND protocol='v2'")
    e = running[0] if running else None
    if not e:
        for c in rows(conn, "SELECT * FROM candidates WHERE status='dev_ok' AND submission_id IS NOT NULL AND submission_id != ? ORDER BY priority DESC", (ctrl,)):
            if not live:
                summary['plan'].append(dict(action='open_experiment', candidate=c['name'], control=ctrl))
                break
            e = open_experiment(conn, root, cfg, snap, actor, c, summary)
            if e:
                break
    if not e:
        return
    params = effective_params(conn, loads(e['params'], DEFAULT_PARAMS) or DEFAULT_PARAMS)
    blocks, results = legacy_shapes(conn, e['id'])
    paired = stats.paired_blocks_v2(blocks, results)
    by_id = {p['block']: p for p in paired}
    maps_n = len(rotation(loads(e['map_ids'], []))) if request_shape(conn, params) == 'double' else len(loads(e['map_ids'], []))
    # 3a-i. blocks that lost an arm (deferred, rejected or released): request the missing arm first
    for b in blocks:
        pending = rows(conn, "SELECT submission FROM requests WHERE block_id=? AND status IN ('reserved','accepted')", (b['id'],))
        have = {r['submission'] for r in pending}
        if b['control'] in have and b['candidate'] in have:
            continue
        if len(have) >= 2 or any(i['payload'].get('request_id') in {r['id'] for r in rows(conn, 'SELECT id FROM requests WHERE block_id=?', (b['id'],))} for i in open_intents(conn)):
            continue
        missing_arm = next((sid for sid in (b['control'], b['candidate']) if sid not in have), None)
        if missing_arm is None:
            continue
        req_maps = b.get('request_maps') or b['map_ids']
        if q['field']['available'] < len(req_maps) or (missing_arm != snap.active and in_blackout(cfg, snap.now)):
            summary['deferred'].append(dict(reason='missing_arm_wait', block=b['id'], arm=missing_arm))
            continue
        summary['plan'].append(dict(action='missing_arm', block=b['id'], arm=missing_arm))
        if live:
            waves = waves_of_distinct_maps(req_maps)
            ids = request_batch(conn, root, cfg, snap, client, actor, missing_arm, b['opponent'], waves[0], 'field', b['id'], summary, waves=waves[1:])
            if ids:
                q['field']['available'] -= len(ids)
            elif summary.get('request_shape_refused'):
                conn.execute("UPDATE blocks SET excluded_reason=?, updated_at=? WHERE id=?", ('20-map request refused by the server; re-planned as single-orientation blocks', now_iso(), b['id']))
                return
    blocks, results = legacy_shapes(conn, e['id'])
    paired = stats.paired_blocks_v2(blocks, results)
    by_id = {p['block']: p for p in paired}
    # 3a-ii. fills for incomplete blocks whose games are all harvested
    for b in blocks:
        p = by_id.get(b['id'])
        if not p or p['complete']:
            continue
        ids = [i for g in b['requests'] for i in g]
        if any(not results.get(str(i)) for i in ids):
            continue  # still harvesting
        if b['fill_attempts'] >= params['max_fills']:
            if len(p['pairs']) >= params['min_pairs']:
                continue  # accepted by the min_pairs rule: the pairs it has are used as they are
            summary['plan'].append(dict(action='exclude_block', block=b['id'], pairs=len(p['pairs'])))
            if live:
                conn.execute("UPDATE blocks SET excluded_reason=?, updated_at=? WHERE id=?", (f"{len(p['pairs'])} pairs after {params['max_fills']} fills (min {params['min_pairs']})", now_iso(), b['id']))
                db.event(conn, root, actor, 'block_excluded', dict(block=b['id'], pairs=len(p['pairs'])))
            continue
        # a fill is paired (D-022): both arms request the missing maps back to back, the second arm's waves aligned so that
        # consecutive ids give the two arms the same starting layouts whatever parity they land on (single-arm fills only
        # pair by luck, and never when the arm's parity is locked by regular foreign traffic)
        paired_fill = request_shape(conn, params) == 'double'
        arms = list(b.get('order') or [b['control'], b['candidate']]) if paired_fill else [[b['candidate'], b['control']][b['fill_attempts'] % 2]]
        if q['field']['available'] < len(arms) * len(p['missing_maps']):
            summary['deferred'].append(dict(reason='quota', block=b['id']))
            continue
        summary['plan'].append(dict(action='fill', block=b['id'], arms=arms, maps=p['missing_maps']))
        if live:
            conn.execute('UPDATE blocks SET fill_attempts=fill_attempts+1, updated_at=? WHERE id=?', (now_iso(), b['id']))
            waves = waves_of_distinct_maps(spread(p['missing_maps']))
            for k, arm in enumerate(arms):
                arm_waves = [aligned(w, k, b['map_ids']) for w in waves]
                ids = request_batch(conn, root, cfg, snap, client, actor, arm, b['opponent'], arm_waves[0], 'field', b['id'], summary, waves=arm_waves[1:])
                if ids:
                    q['field']['available'] -= len(ids)
    # 3b. the next block: both arms in the same cycle or not at all
    d = decide(blocks, results, params)
    phase = 'confirm' if d['verdict'] == 'confirming' else 'screen' if d['verdict'] == 'screening' else None
    if phase is None:
        return
    target = params['confirm_blocks'] if phase == 'confirm' else params['screen_blocks']
    current = [b for b in blocks if b['phase'] == phase]
    if len(current) >= target:
        return
    panel = loads(e['confirmation_opponents'] if phase == 'confirm' else e['screen_opponents'], [])
    used = {b['opponent'] for b in current}
    excluded = {r['team_id'] for r in rows(conn, 'SELECT team_id FROM opponent_exclusions WHERE until>?', (snap.now,))}
    opponent = next((o for o in panel if o not in used and o not in excluded), None)
    if opponent is None:
        summary['attention'].append(dict(kind='panel_exhausted', experiment=e['id'], phase=phase))
        return
    if q['field']['available'] < 2 * maps_n:
        summary['deferred'].append(dict(reason='quota_for_both_arms', experiment=e['id'], phase=phase, need=2 * maps_n, have=q['field']['available']))
        return
    if snap.active != e['control_submission']:
        return
    if in_blackout(cfg, snap.now):
        summary['deferred'].append(dict(reason='ranked_exposure_blackout', experiment=e['id'], phase=phase))
        return
    if ranked_in_flight(snap):
        summary['deferred'].append(dict(reason='ranked_series_in_flight', series=ranked_in_flight(snap), experiment=e['id'], phase=phase))
        return
    summary['plan'].append(dict(action='block', experiment=e['id'], phase=phase, opponent=opponent, games_per_arm=maps_n, shape=request_shape(conn, params)))
    if live:
        b = new_block(conn, e, phase, opponent, params)
        waves = waves_of_distinct_maps(b['request_maps'])
        for sid in b['order']:
            ids = request_batch(conn, root, cfg, snap, client, actor, sid, opponent, waves[0], 'field', b['id'], summary, waves=waves[1:])
            if ids:
                q['field']['available'] -= len(ids)
            elif summary.get('request_shape_refused'):
                conn.execute("UPDATE blocks SET excluded_reason=?, updated_at=? WHERE id=?", ('20-map request refused by the server; re-planned as single-orientation blocks', now_iso(), b['id']))
                return


def upload(conn, root, cfg, snap, client, actor, cand, summary):
    import zipfile
    archive = Path(cand['archive_path'])
    files = loads(cand['source_files'], {}) or {}
    with zipfile.ZipFile(archive) as z:
        packed = {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
    if packed != files:
        conn.execute("UPDATE candidates SET status='retired', retired_reason='archive mismatch', updated_at=? WHERE name=?", (now_iso(), cand['name']))
        raise Stop(f"candidate {cand['name']} archive does not match its frozen files")
    name = f"LV-{cand['name']}-{cand['fingerprint'][:8]}-ai"
    prior = [s for s in snap.subs if s.get('name') == name]
    if prior:
        conn.execute("UPDATE candidates SET submission_id=?, upload_name=?, status='uploaded', updated_at=? WHERE name=?", (prior[0]['id'], name, now_iso(), cand['name']))
        return
    if snap.active != control(conn):
        return
    boundary = 'hub' + uuid.uuid4().hex
    parts = []
    lang = {'python': 'python', 'cpp': 'cpp', 'c': 'c'}[cand['language']]
    for key, value in {'name': name, 'language': lang, 'description': 'Automated unranked validation; frozen candidate ' + cand['fingerprint']}.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="zip"; filename="bot.zip"\r\nContent-Type: application/zip\r\n\r\n'.encode() + archive.read_bytes() + b'\r\n')
    parts.append(f'--{boundary}--\r\n'.encode())
    tid = open_tx(conn, 'upload', dict(name=name, fingerprint=cand['fingerprint'], previous=snap.active, candidate=cand['name']))
    try:
        mutate(conn, client, 'upload', '/api/v1/submissions', b''.join(parts), 'upload ' + name, dict(name=name, fingerprint=cand['fingerprint']), 'multipart/form-data; boundary=' + boundary)
    except APIError as e:
        if 400 <= e.status < 500:
            close_tx(conn, tid, f'rejected {e.status}')
            conn.execute("UPDATE candidates SET status='retired', retired_reason=?, updated_at=? WHERE name=?", (f'upload rejected {e.status}: {e.message[:120]}', now_iso(), cand['name']))
            return
        raise
    except UncertainMutation:
        raise Stop('upload acknowledgement lost; reconciled by exact name next cycle')
    db.event(conn, root, actor, 'uploaded', dict(candidate=cand['name'], name=name))
    summary['uploads'].append(dict(name=name, candidate=cand['name'], pending=True))


# ----------------------------------------------------------------------------------------------- the cycle
def migrate_params(conn, root, actor, summary):
    """Running v2 experiments opened with parameters a later decision replaced (D-022: fills) take the new values; the
    change is recorded as an event and in the summary. Closed experiments keep the parameters they were decided under.
    Accepted requests whose recorded count exceeds the games the server created (the 20-entry requests of 28 Sep) are
    corrected, so the executor's own hourly cap counts games, not entries."""
    for r in rows(conn, "SELECT id, count, game_ids FROM requests WHERE status='accepted'"):
        n = len(loads(r['game_ids'], []) or [])
        if r['count'] != n:
            conn.execute('UPDATE requests SET count=?, updated_at=? WHERE id=?', (n, now_iso(), r['id']))
            db.event(conn, root, actor, 'request_count_corrected', dict(request=r['id'], recorded=r['count'], games=n))
    # blocks excluded by the pre-D-022 rule (no fills allowed, 14 pairs required) while their games were still unverified
    # are reinstated: the fill logic now completes them
    for b in rows(conn, "SELECT b.id, b.excluded_reason FROM blocks b JOIN experiments e ON e.id=b.experiment_id WHERE e.status='running' AND e.protocol='v2' AND b.excluded_reason LIKE '%after 0 fills (min 14)'"):
        conn.execute('UPDATE blocks SET excluded_reason=NULL, updated_at=? WHERE id=?', (now_iso(), b['id']))
        db.event(conn, root, actor, 'block_reinstated', dict(block=b['id'], was=b['excluded_reason']))
        summary.setdefault('migrated', []).append(dict(block=b['id'], reinstated=b['excluded_reason']))
    for e in rows(conn, "SELECT id, params FROM experiments WHERE status='running' AND protocol='v2'"):
        params = loads(e['params'], None) or dict(DEFAULT_PARAMS)
        changed = {}
        for old, new in zip(PARAMS_MIGRATIONS[::2], PARAMS_MIGRATIONS[1::2]):
            if all(params.get(k) == v for k, v in old.items()):
                changed.update(new)
        if changed:
            conn.execute('UPDATE experiments SET params=?, updated_at=? WHERE id=?', (db.j(dict(params, **changed)), now_iso(), e['id']))
            db.event(conn, root, actor, 'params_migrated', dict(experiment=e['id'], changed=changed))
            summary.setdefault('migrated', []).append(dict(experiment=e['id'], changed=changed))


def run_cycle(conn, root, cfg, client, mode='shadow', actor='hub/executor', now=None, progress=None):
    """One reconciling cycle. `progress(phase, detail)` is called at phase boundaries and during long phases so the
    daemon can mirror what a slow server is costing (the cadence is a minimum gap between cycle starts, not a deadline)."""
    now = now or time.time()
    CLOCK['now'] = now
    ensure_columns(conn)
    progress = progress or (lambda phase, detail=None: None)
    started = time.monotonic()
    summary = dict(at=now_iso(), mode=mode, external_actions=[], reconciled=[], frozen=[], uploads=[], harvest_errors=[], verdicts=[], plan=[], dispatched=[], deferred=[], attention=[], opened=[], stop=None)
    try:
        snap = Snapshot(client, conn, cfg, now, progress=progress)
    except Stop as s:
        summary['stop'] = str(s)
        summary['attention'].append(dict(kind='snapshot_failed', detail=str(s)))
        return summary
    summary['active'] = snap.active
    summary['ranked_recent'] = ranked_recent(snap)
    if snap.history_incomplete:
        summary['attention'].append(dict(kind='quota_unknown', detail='history refresh cut short by the snapshot budget; no requests this cycle'))
    progress('reconcile')
    try:
        observe_control(conn, root, cfg, snap, actor, summary)
        reconcile(conn, root, cfg, snap, client, actor, summary)
    except Stop as s:
        summary['stop'] = str(s)
    progress('harvest')
    harvest(conn, root, cfg, snap, client, actor, summary)
    summary['control'] = control(conn)
    q = quota(conn, cfg, snap)
    summary['quota'] = q
    if summary['stop']:
        summary['seconds'] = round(time.monotonic() - started)
        return summary
    progress('plan')
    if summary.get('pending_restore') and mode == 'live':
        p = summary['pending_restore']
        if restore(conn, root, cfg, snap, client, actor, p['previous'], p['candidate'], p.get('reason', 'restore of an open switch')):
            snap.active = p['previous']
            if control(conn) == p['candidate']:
                set_control(conn, root, actor, p['previous'], 'restored', p.get('reason', 'restore'))
                summary['control'] = p['previous']
        for tx in open_txs(conn, 'switch'):
            close_tx(conn, tx['id'], 'restored by cycle')
    try:
        migrate_params(conn, root, actor, summary)
        monitor_probation(conn, root, cfg, snap, client, actor, summary)
        evaluate(conn, root, cfg, snap, client, actor, summary)
        plan_and_dispatch(conn, root, cfg, snap, client, actor, q, summary)
    except Stop as s:
        summary['stop'] = str(s)
    summary['seconds'] = round(time.monotonic() - started)
    db.kv_set(conn, 'executor_last', {k: v for k, v in summary.items() if k != 'plan'} | {'plan_n': len(summary['plan'])})
    db.event(conn, root, actor, 'executor_cycle', dict(mode=mode, active=summary.get('active'), control=summary.get('control'), dispatched=len(summary['dispatched']),
                                                       verdicts=summary['verdicts'], stop=summary['stop'], attention=[a['kind'] for a in summary['attention']]))
    return summary
