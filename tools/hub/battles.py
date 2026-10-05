"""Targeted requested battles: `<mirror>/control/battles.json`, answered by `battles.done.json` (Live ops, Phase 3).

A request names one or more arms (our submissions or registered candidates), a roster of opponent teams, maps and
seats, and a games budget; it must cite the Chair's D-record. Accepted requests become durable *jobs* (table
`battle_jobs`) that the actuator dispatches in small units across loops, inside the rolling-hour allowance:

    {"label": "p2-screen-1", "by": "claude/daichi/…", "decision": "D-046", "note": "…",
     "arms": [{"submission": 14585}, {"candidate": "learner-01-bc-prior"}],     # or "submission"/"candidate" for one arm
     "opponents": [45, 133], "maps": ["Trauma", "Maze"],                        # omit maps = every active map
     "seats": "both", "games_per_pair": 2, "max_games": 120, "deadline_hours": 24}

Other actions on the same file: {"action": "enable"|"disable", "by", "decision"} (dispatch is off until the Chair
enables it), {"action": "cancel", "job": id, "by", "note"}.

Dispatch rules (all from the executor, reused rather than re-implemented):
- every unit goes through `executor.request_batch` (reserve → [temporary activation] → POST → restore), so a
  non-active arm is active only for the seconds of its POST, never in the ranked blackout around even hours and
  never while one of our ranked series is in flight;
- a unit is one opponent × one chunk of maps for *every* arm, back to back, arm order shuffled per unit; with
  `seats: both` each arm posts the chunk twice (rotation, D-022), so each map is played at both id parities (the
  starting layout is f(map, id parity), A1-Q3);
- a unit is dispatched only when the whole unit fits the pool's available allowance minus `reserve_games`
  (teammates and the collector share the key), and at most `cycle_games` per loop;
- a job pauses if the live submission is no longer the one it was accepted under (a human activation pauses all
  automation, D-045/Live-ops rule), and expires at its deadline;
- an open switch whose restore was lost is restored here before anything else (the shadow executor never does).

Games are harvested and verified by the executor's existing harvest (it runs in shadow mode too); they carry
`block_id = 'job:<id>'`. The corpus collector watches team 7, so the replays also reach `public_replays/corpus`.
`status()` mirrors every job, with per-game rows, to `<mirror>/battles/`.
"""
import json
import random
import time
import uuid
from pathlib import Path

from . import db, executor

SCHEMA = """
CREATE TABLE IF NOT EXISTS battle_jobs(id TEXT PRIMARY KEY, created_at TEXT, updated_at TEXT, label TEXT, by TEXT,
  decision TEXT, body TEXT, status TEXT, expect_active INTEGER, units TEXT, next_unit INTEGER DEFAULT 0,
  games_requested INTEGER DEFAULT 0, deadline REAL, note TEXT);
"""
DEFAULTS = dict(interval_seconds=300, cycle_games=40, chunk_maps=5, reserve_games={'field': 5, 'dev': 5},
                max_job_games=600)
ACTOR = 'hub/battles'


def settings(cfg):
    out = dict(DEFAULTS)
    out.update(cfg.get('battles') or {})
    return out


def ensure(conn):
    conn.executescript(SCHEMA)


def enabled(conn):
    return bool((db.kv_get(conn, 'battles_enabled') or {}).get('enabled'))


# ------------------------------------------------------------------------------------------------ planning
def chunks(maps, size):
    size = max(1, int(size))
    return [maps[i:i + size] for i in range(0, len(maps), size)]


def arm_waves(chunk, seats, games_per_pair):
    """Map waves for one arm on one chunk. `both` seats: the D-022 rotation, repeated games_per_pair/2 times."""
    if seats == 'both':
        reps = max(1, games_per_pair // 2)
        return [w for _ in range(reps) for w in executor.waves_of_distinct_maps(executor.rotation(chunk))]
    return [list(chunk) for _ in range(max(1, games_per_pair))]


def plan_units(job_id, arms, opponents, map_ids, seats, games_per_pair, chunk_maps):
    """Units interleave opponents within each chunk so a partly dispatched job stays balanced across the roster."""
    units = []
    for ci, chunk in enumerate(chunks(list(map_ids), chunk_maps)):
        for opp in opponents:
            order = list(arms)
            random.Random(f'{job_id}:{ci}:{opp}').shuffle(order)
            waves = arm_waves(chunk, seats, games_per_pair)
            units.append(dict(opponent=opp, chunk=ci, maps=list(chunk), arms=order, waves=waves,
                              games=len(order) * sum(len(w) for w in waves)))
    return units


def validate(conn, body, snap, cfg):
    """Returns (job_row, units) or raises ValueError with the reason."""
    s = settings(cfg)
    for field in ('by', 'decision', 'label'):
        if not str(body.get(field) or '').strip():
            raise ValueError(f'{field} is required (a targeted test needs a Chair D-record, a label and an author)')
    raw_arms = body.get('arms') or [{k: body[k]} for k in ('submission', 'candidate') if body.get(k) is not None]
    if not raw_arms:
        raise ValueError('no arm: give "arms", "submission" or "candidate"')
    ours = {s_['id']: s_ for s_ in snap.subs}
    arms = []
    for a in raw_arms:
        if a.get('candidate') is not None:
            row = conn.execute('SELECT submission_id FROM candidates WHERE name=?', (a['candidate'],)).fetchone()
            if not row or row['submission_id'] is None:
                raise ValueError(f"candidate {a['candidate']!r} is not registered and uploaded")
            sid = int(row['submission_id'])
        else:
            sid = int(a['submission'])
        if sid not in ours:
            raise ValueError(f'submission {sid} is not one of ours on the server')
        arms.append(sid)
    if len(set(arms)) != len(arms):
        raise ValueError('duplicate arm')
    opponents = [int(x) for x in body.get('opponents') or []]
    if not opponents or snap.team_id in opponents:
        raise ValueError('opponents must be a non-empty list of other teams')
    by_name = {m.get('name'): m['id'] for m in snap.maps}
    names = body.get('maps')
    if names in (None, 'all', []):
        map_ids = list(snap.map_ids)
    else:
        unknown = [n for n in names if n not in by_name]
        if unknown:
            raise ValueError(f'unknown or inactive maps: {unknown}')
        map_ids = list(dict.fromkeys(by_name[n] for n in names))
    seats = body.get('seats', 'both')
    if seats not in ('both', 'one'):
        raise ValueError('seats must be "both" or "one"')
    gpp = int(body.get('games_per_pair', 2 if seats == 'both' else 1))
    if seats == 'both' and (gpp < 2 or gpp % 2):
        raise ValueError('games_per_pair must be even and ≥ 2 with seats "both"')
    jid = uuid.uuid4().hex[:12]
    units = plan_units(jid, arms, opponents, map_ids, seats, gpp, s['chunk_maps'])
    total = sum(u['games'] for u in units)
    cap = min(int(body.get('max_games') or total), int(s['max_job_games']))
    if total > cap:
        raise ValueError(f'plan needs {total} games, over max_games/max_job_games {cap}; shrink the roster or maps')
    deadline = snap.now + float(body.get('deadline_hours', 24)) * 3600
    job = dict(id=jid, created_at=db.now_iso(), label=str(body['label'])[:80], by=str(body['by'])[:120], decision=str(body['decision'])[:40],
               body=dict(body, arms_resolved=arms, map_ids=map_ids, seats=seats, games_per_pair=gpp, planned_games=total),
               status='open', expect_active=snap.active, units=units, next_unit=0, games_requested=0, deadline=deadline,
               note=str(body.get('note') or '')[:300])
    return job, units


# ------------------------------------------------------------------------------------------------ control file
def handle_request(conn, root, cfg, mirror, snap_factory, log=print):
    """Read `battles.json` once, answer in `battles.done.json`, remove the request. `snap_factory()` -> Snapshot."""
    ensure(conn)
    ctl = Path(mirror) / 'control'
    req = ctl / 'battles.json'
    if not req.exists():
        return None
    try:
        body = json.loads(req.read_text())
    except ValueError:
        body = None
    out = dict(at=db.now_iso())
    try:
        if not isinstance(body, dict):
            raise ValueError('request is not a JSON object')
        action = body.get('action', 'submit')
        out['action'] = action
        if action in ('enable', 'disable'):
            if not body.get('by') or not body.get('decision'):
                raise ValueError('enable/disable needs "by" and the Chair\'s "decision"')
            state = dict(enabled=action == 'enable', by=body['by'], decision=body['decision'], at=db.now_iso())
            db.kv_set(conn, 'battles_enabled', state)
            db.event(conn, root, body['by'], 'battles_' + action, state)
            out['enabled'] = state['enabled']
        elif action == 'cancel':
            n = conn.execute("UPDATE battle_jobs SET status='cancelled', updated_at=? WHERE id=? AND status IN ('open','paused')",
                             (db.now_iso(), body.get('job'))).rowcount
            if not n:
                raise ValueError(f"no open job {body.get('job')!r}")
            db.event(conn, root, body.get('by') or 'unknown', 'battles_cancel', dict(job=body.get('job'), note=body.get('note')))
            out['job'] = body.get('job')
            out['cancelled'] = True
        elif action == 'submit':
            snap = snap_factory()
            job, units = validate(conn, body, snap, cfg)
            db.upsert(conn, 'battle_jobs', job, 'id')
            db.event(conn, root, job['by'], 'battles_job_accepted', dict(job=job['id'], label=job['label'], decision=job['decision'],
                                                                       arms=job['body']['arms_resolved'], games=job['body']['planned_games']))
            out.update(job=job['id'], accepted=True, units=len(units), planned_games=job['body']['planned_games'],
                       arms=job['body']['arms_resolved'], expect_active=job['expect_active'], dispatch_enabled=enabled(conn))
        else:
            raise ValueError(f'unknown action {action!r}')
    except Exception as exc:
        out['error'] = f'{type(exc).__name__}: {str(exc)[:300]}'
    ctl.mkdir(parents=True, exist_ok=True)
    (ctl / 'battles.done.json').write_text(json.dumps(out, indent=1, default=str))
    req.unlink(missing_ok=True)
    log(f'battles request: {out}')
    return out


# ------------------------------------------------------------------------------------------------ dispatch
def open_jobs(conn):
    ensure(conn)
    return [db.loads_row(r, 'body', 'units') for r in db.rows(conn, "SELECT * FROM battle_jobs WHERE status IN ('open','paused') ORDER BY created_at")]


def restore_lost_switches(conn, root, cfg, snap, client, summary):
    """A switch left open by a lost restore: put the previous submission back (only if the candidate is still active)."""
    for tx in executor.open_txs(conn, 'switch'):
        p = tx['payload']
        if snap.active == p.get('candidate'):
            if executor.restore(conn, root, cfg, snap, client, ACTOR, p['previous'], p['candidate'], 'battles: restore a lost switch'):
                snap.active = p['previous']
                executor.close_tx(conn, tx['id'], 'restored by battles')
                summary['restored'].append(p)
            else:
                summary['attention'].append(dict(kind='switch_unresolved', tx=tx['id']))
        elif snap.active == p.get('previous'):
            executor.close_tx(conn, tx['id'], 'restored')
        else:
            executor.close_tx(conn, tx['id'], 'external_choice_preserved', dict(p, observed=snap.active))
    return not executor.open_txs(conn, 'switch')


def tick(conn, root, cfg, client, snap=None, now=None, notify=None):
    """One dispatch pass over open jobs. Returns a summary; never raises for an expected refusal."""
    ensure(conn)
    s = settings(cfg)
    now = now or time.time()
    summary = dict(at=db.now_iso(), dispatched=[], deferred=[], attention=[], restored=[], jobs={})
    jobs = open_jobs(conn)
    pending_switch = executor.open_txs(conn, 'switch')
    if not jobs and not pending_switch:
        return summary
    executor.CLOCK['now'] = now
    try:
        snap = snap or executor.Snapshot(client, conn, cfg, now)
        if not restore_lost_switches(conn, root, cfg, snap, client, summary):
            summary['deferred'].append(dict(reason='open_switch'))
            return summary
        if not enabled(conn):
            summary['deferred'].append(dict(reason='dispatch_disabled'))
            return summary
        if executor.open_intents(conn):
            summary['deferred'].append(dict(reason='open_intents'))
            return summary
        if snap.history_incomplete:
            summary['deferred'].append(dict(reason='quota_unknown'))
            return summary
        q = executor.quota(conn, cfg, snap)
        budget = int(s['cycle_games'])
        for job in jobs:
            jid = job['id']
            if now > (job['deadline'] or 0):
                conn.execute("UPDATE battle_jobs SET status='expired', updated_at=? WHERE id=?", (db.now_iso(), jid))
                summary['jobs'][jid] = 'expired'
                continue
            if snap.active != job['expect_active']:
                if job['status'] != 'paused':
                    conn.execute("UPDATE battle_jobs SET status='paused', updated_at=? WHERE id=?", (db.now_iso(), jid))
                    summary['attention'].append(dict(kind='battles_paused_external_activation', job=jid, expected=job['expect_active'], active=snap.active))
                    if notify:
                        notify('battles_paused', f"job {jid} ({job['label']}): live submission is {snap.active}, expected {job['expect_active']}; paused")
                summary['jobs'][jid] = 'paused'
                continue
            if job['status'] == 'paused':
                conn.execute("UPDATE battle_jobs SET status='open', updated_at=? WHERE id=?", (db.now_iso(), jid))
            units = job['units'] or []
            k = job['next_unit'] or 0
            while k < len(units):
                u = units[k]
                pool = executor.pool_of(snap, u['opponent'])
                reserve = int((s['reserve_games'] or {}).get(pool, 0))
                if u['games'] > budget or u['games'] > q[pool]['available'] - reserve:
                    summary['deferred'].append(dict(reason='quota', job=jid, unit=k, pool=pool, need=u['games'], available=q[pool]['available'], reserve=reserve, budget=budget))
                    break
                foreign = [a for a in u['arms'] if a != snap.active]
                if foreign and executor.in_blackout(cfg, snap.now):
                    summary['deferred'].append(dict(reason='ranked_exposure_blackout', job=jid, unit=k))
                    break
                if foreign and executor.ranked_in_flight(snap):
                    summary['deferred'].append(dict(reason='ranked_series_in_flight', job=jid, unit=k))
                    break
                got = 0
                inner = dict(deferred=[], attention=[], dispatched=[])
                for arm in u['arms']:
                    ids = executor.request_batch(conn, root, cfg, snap, client, ACTOR, arm, u['opponent'], u['waves'][0], pool, f'job:{jid}', inner, waves=u['waves'][1:])
                    got += len(ids or [])
                    if ids is None:
                        break
                summary['attention'].extend(inner['attention'])
                summary['deferred'].extend(inner['deferred'])
                summary['dispatched'].extend(dict(d, job=jid, unit=k) for d in inner['dispatched'])
                q[pool]['available'] -= got
                budget -= got
                k += 1   # a unit is attempted once: a refused arm leaves an unpaired cell, reported, not re-posted
                conn.execute('UPDATE battle_jobs SET next_unit=?, games_requested=games_requested+?, updated_at=? WHERE id=?', (k, got, db.now_iso(), jid))
                if any(a.get('kind') in ('quota_rejection', 'restore_uncertain') for a in inner['attention']):
                    break
            if k >= len(units):
                conn.execute("UPDATE battle_jobs SET status='dispatched', updated_at=? WHERE id=?", (db.now_iso(), jid))
            summary['jobs'][jid] = f'{k}/{len(units)} units'
            if budget <= 0:
                break
    except executor.Stop as exc:
        summary['attention'].append(dict(kind='battles_stop', detail=str(exc)[:200]))
    finally:
        executor.CLOCK['now'] = None
    db.event(conn, root, ACTOR, 'battles_tick', {k: v for k, v in summary.items() if k != 'jobs'} | dict(jobs=summary['jobs']))
    return summary


# ------------------------------------------------------------------------------------------------ evidence
def job_games(conn, jid):
    """Every requested game of a job with its harvest state; parity = game id % 2 (the seat/layout key, A1-Q3)."""
    out = []
    for r in db.rows(conn, "SELECT * FROM requests WHERE block_id=? ORDER BY at", (f'job:{jid}',)):
        for gid in json.loads(r['game_ids'] or '[]'):
            g = conn.execute('SELECT verified, error, score, map_id, map_name, faults, caught_errors, cpu_max, reason, rounds, api_side, requested_at, seed, opponent_submission FROM games WHERE game_id=?', (gid,)).fetchone()
            g = dict(g) if g else {}
            out.append(dict(game_id=gid, arm=r['submission'], opponent=r['opponent_team'], pool=r['pool'], parity=gid % 2,
                            map_id=g.get('map_id'), map_name=g.get('map_name'), verified=bool(g.get('verified')), error=g.get('error'),
                            score=g.get('score'), faults=g.get('faults'), caught_errors=g.get('caught_errors'), cpu_max=g.get('cpu_max'),
                            reason=g.get('reason'), rounds=g.get('rounds'), side=g.get('api_side'),
                            # D-056 §B: opponent submission id per game. The API has carried no submission ids since 28 Sep
                            # (D-023), so this is null unless the server restores them; request_at (one unit's arms are
                            # posted seconds apart) is the recorded proxy for "same opponent version".
                            opponent_submission=g.get('opponent_submission'), request_at=r['at'], requested_at=g.get('requested_at'), seed=g.get('seed')))
    return out


# D-060 §C: the server exposes no opponent submission id, so a pair counts as matched by proxy (both arms' games
# posted in the same unit, seconds apart). Every report says so.
MATCHING = 'proxy: same unit (no opponent submission id on the server; D-060 §C)'


def paired_report(games, arms, resamples=1000, seed=7):
    """Candidate − reference, paired by (opponent, map, parity); cluster bootstrap over opponents (series).
    Missing or unverified games drop their cell (counted, never scored as losses). Interval: 5th–95th percentile."""
    if len(arms) < 2:
        return None
    ref, cand = arms[0], arms[1]
    cells = {}
    for g in games:
        if not g['verified'] or g['score'] is None or g['map_id'] is None:
            continue
        cells.setdefault((g['opponent'], g['map_id'], g['parity']), {}).setdefault(g['arm'], []).append(g['score'])
    diffs = {}
    for (opp, m, p), by_arm in cells.items():
        if ref in by_arm and cand in by_arm:
            d = sum(by_arm[cand]) / len(by_arm[cand]) - sum(by_arm[ref]) / len(by_arm[ref])
            diffs.setdefault(opp, []).append(d)
    n = sum(len(v) for v in diffs.values())
    if not n:
        return dict(reference=ref, candidate=cand, pairs=0, matching=MATCHING)
    point = sum(sum(v) for v in diffs.values()) / n
    rng = random.Random(seed)
    opps = sorted(diffs)
    boots = []
    for _ in range(resamples):
        pick = [rng.choice(opps) for _ in opps]
        tot = sum(sum(diffs[o]) for o in pick)
        cnt = sum(len(diffs[o]) for o in pick)
        boots.append(tot / cnt)
    boots.sort()
    return dict(reference=ref, candidate=cand, pairs=n, clusters=len(opps), delta=round(point, 4),
                lo5=round(boots[int(0.05 * resamples)], 4), hi95=round(boots[int(0.95 * resamples) - 1], 4),
                per_opponent={o: dict(pairs=len(v), delta=round(sum(v) / len(v), 3)) for o, v in diffs.items()},
                interval='cluster bootstrap over opponents, 1000 resamples, seed 7, 5th/95th percentile', matching=MATCHING)


def blind(report, job_status):
    """D-056 §C.7 / D-063 §B: no interim reads. While a job is open the mirrored summary carries only the pair and
    cluster counts (for the look schedule); delta, interval and per-opponent figures appear once the job is closed.
    Per-game rows still carry scores, so the job file is not a blind store; it just stops showing a running figure."""
    if report is None or job_status != 'open':
        return report
    return dict(reference=report['reference'], candidate=report['candidate'], pairs=report['pairs'],
                clusters=report.get('clusters', 0), withheld='open job: no interim paired figures (D-056 §C.7, D-063 §B)',
                matching=report.get('matching'))


def request_counts(conn, jid):
    """Per-job request rows by status, so server-rejected units are visible in the index (a rejected unit is
    attempted once and leaves unpaired cells; it is reported here, never counted as a loss)."""
    out = dict(requests={}, rejected_opponents=[])
    for r in db.rows(conn, 'SELECT status, opponent_team FROM requests WHERE block_id=?', (f'job:{jid}',)):
        out['requests'][r['status']] = out['requests'].get(r['status'], 0) + 1
        if r['status'] == 'rejected' and r['opponent_team'] not in out['rejected_opponents']:
            out['rejected_opponents'].append(r['opponent_team'])
    return out


def status(conn, mirror):
    """Mirror every job (and its games) to `<mirror>/battles/`, plus an index `battles/index.json`."""
    ensure(conn)
    out_dir = Path(mirror) / 'battles'
    out_dir.mkdir(parents=True, exist_ok=True)
    index = dict(at=db.now_iso(), enabled=db.kv_get(conn, 'battles_enabled'), jobs=[])
    for r in db.rows(conn, 'SELECT * FROM battle_jobs ORDER BY created_at DESC LIMIT 50'):
        job = db.loads_row(r, 'body', 'units')
        games = job_games(conn, job['id'])
        arms = job['body'].get('arms_resolved') or []
        summary = dict(id=job['id'], label=job['label'], by=job['by'], decision=job['decision'], status=job['status'], arms=arms,
                       expect_active=job['expect_active'], units=f"{job['next_unit']}/{len(job['units'] or [])}",
                       planned=job['body'].get('planned_games'), requested=len(games), verified=sum(g['verified'] for g in games),
                       unverified=sum(1 for g in games if not g['verified']), runtime_faults=sum(1 for g in games if (g['faults'] or 0) or (g['caught_errors'] or 0)),
                       paired=blind(paired_report(games, arms), job['status']), **request_counts(conn, job['id']))
        index['jobs'].append(summary)
        (out_dir / f"{job['id']}.json").write_text(json.dumps(dict(summary, request=job['body'], games=games), indent=1, default=str))
    (out_dir / 'index.json').write_text(json.dumps(index, indent=1, default=str))
    return index
