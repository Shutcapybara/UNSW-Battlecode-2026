"""The hub daemon: 60 s safety loop + 600 s evidence/decision cycle, legacy keep-alive, notifications.

Observer mode only on day one: it never calls a mutating API endpoint. `HUB/control/stop` stops it gracefully.
Run: `python -m hub.actuator --serve` (deployed copy) or `python -m tools.hub.actuator --once --packet` (repo).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import db
from .config import hub_root, load_config
from .cycle import parse_iso, run_cycle
from .gitkeeper import sync as git_sync
from .legacy_ops import watchdog as legacy_watchdog
from . import executor as hub_executor
from . import corpus as hub_corpus


from collections import deque
RECENT = deque(maxlen=30)
RECENT_ERRORS = deque(maxlen=10)


def write_health(root, cfg, state, extra=None):
    """`<mirror>/daemon.json`: what the daemon is doing, readable from any session that mounts the repository."""
    try:
        conn = db.connect(root)
        body = dict(at=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), mode=state.get('mode'), configured=state.get('configured'),
                    app=str(Path(__file__).resolve().parent.parent), shadow_clean=db.kv_get(conn, 'executor_shadow_clean'), cutover=db.kv_get(conn, 'cutover'),
                    cutover_pending=bool(state.get('cutover_pending')), cutover_started=state.get('cutover_started'), legacy_adopted=bool(db.kv_get(conn, 'legacy_adopted')),
                    control=db.kv_get(conn, 'control'), control_owner=db.kv_get(conn, 'control_owner'), executor_last=db.kv_get(conn, 'executor_last'),
                    open_intents=len(hub_executor.open_intents(conn)), open_transactions=len(hub_executor.open_txs(conn)),
                    last_cycle_at=db.kv_get(conn, 'last_cycle_at'), restart=state.get('restart'), recent=list(RECENT), recent_errors=list(RECENT_ERRORS),
                    corpus_last=state.get('corpus_last'), corpus_passes=state.get('corpus_passes', 0), executor_busy=bool(state.get('executor_busy')))
        conn.close()
        if extra:
            body.update(extra)
        out = Path(cfg['paths']['mirror'])
        out.mkdir(parents=True, exist_ok=True)
        tmp = out / 'daemon.json.tmp'
        tmp.write_text(json.dumps(body, indent=1, default=str))
        tmp.replace(out / 'daemon.json')
    except Exception:
        pass


def notify(root, cfg, kind, text):
    root = Path(root)
    (root / 'notify').mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    (root / 'notify' / f'{stamp}-{kind}.md').write_text(f'# {kind}\n\n{text}\n')
    if cfg['notify'].get('osascript') and sys.platform == 'darwin' and shutil.which('osascript'):
        try:
            subprocess.run(['osascript', '-e', f'display notification {json.dumps(text[:200])} with title "JKS hub: {kind}"'], timeout=10, check=False)
        except Exception:
            pass


def legacy_keepalive(root, cfg, log):
    """If the legacy worker has exited (stale status, no stop request) restart it through launchd."""
    live = Path(cfg['paths']['legacy_live'])
    status_path = live / 'state/runner_status.json'
    if not status_path.exists() or not cfg['legacy'].get('keepalive'):
        return None
    try:
        status = json.loads(status_path.read_text())
    except ValueError:
        return None
    at = parse_iso(status.get('at', '') or '')
    if not at:
        return None
    age = time.time() - at
    if age < cfg['legacy']['stale_seconds'] or (live / 'state/runner.stop').exists():
        return None
    if sys.platform != 'darwin' or not shutil.which('launchctl'):
        return dict(action='needed', age=round(age), note='not on macOS; cannot kickstart from here')
    label = cfg['legacy']['launchd_label']
    target = f'gui/{os.getuid()}/{label}'
    result = subprocess.run(['launchctl', 'kickstart', target], capture_output=True, text=True, timeout=30, check=False)
    log(f'legacy keepalive: kickstart {target} rc={result.returncode} {result.stderr.strip()[:120]}')
    return dict(action='kickstart', age=round(age), rc=result.returncode)


def safety_loop_once(root, cfg, state, log):
    """Cheap checks every 60 s: legacy worker health, restoration check, attention changes."""
    live = Path(cfg['paths']['legacy_live'])
    out = {}
    rs = {}
    try:
        rs = json.loads((live / 'state/runner_status.json').read_text())
    except (OSError, ValueError):
        out['legacy'] = 'unreadable'
    reason = (rs.get('attention') or {}).get('reason')
    if reason and reason != state.get('last_attention'):
        notify(root, cfg, 'legacy_attention', reason)
        state['last_attention'] = reason
    if not reason:
        state['last_attention'] = None
    rc = rs.get('active_check') or {}
    if rc and rc.get('matched') is False and rc.get('at') != state.get('last_mismatch'):
        notify(root, cfg, 'active_mismatch', f"active {rc.get('active')} expected {rc.get('expected')} at {rc.get('at')}")
        state['last_mismatch'] = rc.get('at')
    if (cfg.get('executor') or {}).get('mode') == 'live' or state.get('mode') == 'live' or state.get('cutover_pending'):
        out['legacy'] = 'not supervised: executor is live or cutting over (rollback_mac.sh restores the legacy worker)'
        return out
    ka = legacy_keepalive(root, cfg, log)
    if ka:
        out['keepalive'] = ka
        if ka.get('action') == 'kickstart':
            notify(root, cfg, 'legacy_kickstart', f"legacy worker restarted after {ka['age']} s of silence")
    try:
        wd = legacy_watchdog(root, cfg, state, lambda kind, text: notify(root, cfg, kind, text), log)
        if wd:
            out['watchdog'] = wd
    except Exception:
        log('legacy watchdog error\n' + traceback.format_exc())
    return out


def legacy_alive(cfg):
    """True when the legacy worker is loaded in launchd or its status file is fresh: the one-live-executor guard."""
    live = Path(cfg['paths']['legacy_live'])
    try:
        st = json.loads((live / 'state/runner_status.json').read_text())
        if st.get('state') not in ('stopping', 'restarting') and time.time() - parse_iso(st.get('at', '')) < 300:
            return True
    except Exception:
        pass
    if sys.platform == 'darwin' and shutil.which('launchctl'):
        rc = subprocess.run(['launchctl', 'print', f"gui/{os.getuid()}/{cfg['legacy']['launchd_label']}"], capture_output=True, text=True, check=False)
        return rc.returncode == 0
    return False


def take_lease(conn, root):
    row = conn.execute('SELECT * FROM executor_lease WHERE singleton=1').fetchone()
    now = time.time()
    if row and row['expires_at'] > now and row['pid'] != os.getpid():
        try:
            os.kill(row['pid'], 0)
            return None
        except OSError:
            pass
    token = uuid.uuid4().hex
    conn.execute('INSERT OR REPLACE INTO executor_lease(singleton,host,pid,token,acquired_at,expires_at,heartbeat_at) VALUES(1,?,?,?,?,?,?)', (os.uname().nodename, os.getpid(), token, now, now + 300, now))
    return token


def renew_lease(conn, token):
    conn.execute('UPDATE executor_lease SET expires_at=?, heartbeat_at=? WHERE singleton=1 AND token=?', (time.time() + 300, time.time(), token))


def executor_client(cfg):
    from .api import Client
    return Client(cfg['paths']['repo'])


def spawn_preflight(root, cfg, state, log):
    """Run at most one metered probe job at a time, only when the host is not overloaded."""
    proc = state.get('preflight')
    if proc is not None:
        if proc.poll() is None:
            return
        log(f'preflight finished rc={proc.returncode}')
        state['preflight'] = None
    try:
        load = os.getloadavg()[0]
        cores = os.cpu_count() or 4
        if load > 1.5 * cores:
            return
    except (AttributeError, OSError):
        pass
    conn = db.connect(root)
    cand = conn.execute("SELECT name FROM candidates WHERE status='needs_runtime' ORDER BY priority DESC LIMIT 1").fetchone()
    conn.close()
    if not cand:
        return
    (Path(root) / 'logs').mkdir(exist_ok=True)
    out = (Path(root) / 'logs' / f"preflight-{cand['name']}-{int(time.time())}.log").open('w')
    state['preflight'] = subprocess.Popen([sys.executable, '-m', 'hub.preflight' if __package__ == 'hub' else 'tools.hub.preflight', '--candidate', cand['name'], '--root', str(root)], stdout=out, stderr=subprocess.STDOUT, cwd=str(Path(__file__).resolve().parents[1 if __package__ == 'hub' else 2]))
    log(f"preflight started for {cand['name']} pid {state['preflight'].pid}")


def sha256_file(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def legacy_drained(cfg):
    """The legacy worker has no job, no open upload/switch/intent, and is stopping or silent."""
    live = Path(cfg['paths']['legacy_live'])
    try:
        st = json.loads((live / 'state/runner_status.json').read_text())
    except Exception:
        st = {}
    try:
        state = json.loads((live / 'state/state.json').read_text())
    except Exception:
        state = {}
    jobs = list((st.get('jobs') or {}).keys())
    open_tx = [k for k in ('upload', 'switch', 'intent') if state.get(k)]
    at = parse_iso(st.get('at', '') or '')
    quiet = (not at) or time.time() - at > 120
    dead = (not at) or time.time() - at > cfg['legacy'].get('stale_seconds', 300)   # the worker writes status every 5 s; a frozen file is a gone process
    if dead:
        jobs = []   # jobs listed in a frozen status file ended with the process (their controller finishes on its own)
    return dict(ok=not jobs and not open_tx and (quiet or st.get('state') == 'stopping'), jobs=jobs, open=open_tx, state=st.get('state'), quiet=quiet, dead=dead)


def auto_cutover(root, cfg, state, log):
    """Mode 'auto': the daemon performs the cutover itself once the shadow period is clean (see EXECUTOR_V2.md).

    Sequence, one step per safety-loop pass: request the legacy stop -> wait until it drained (no job, no open
    upload/switch/intent) -> unload its LaunchAgent (plist backed up) -> adopt the legacy record -> live. A drain
    that exceeds `drain_timeout_seconds` pages once and keeps waiting; nothing is forced.
    """
    live = Path(cfg['paths']['legacy_live'])
    label = cfg['legacy']['launchd_label']
    stop = live / 'state/runner.stop'
    if not state.get('cutover_started'):
        state['cutover_started'] = time.time()
        if not stop.exists():
            stop.touch()
        conn = db.connect(root)
        db.event(conn, root, 'hub/actuator', 'auto_cutover_started', dict(shadow_clean=db.kv_get(conn, 'executor_shadow_clean')))
        conn.close()
        log('auto-cutover: legacy stop requested; waiting for it to drain')
        notify(root, cfg, 'cutover', 'auto-cutover started: legacy worker asked to stop; executor goes live once it has drained')
        return 'draining'
    d = legacy_drained(cfg)
    if not d['ok']:
        waited = time.time() - state['cutover_started']
        if waited > cfg['executor'].get('drain_timeout_seconds', 1800) and not state.get('cutover_paged'):
            state['cutover_paged'] = True
            notify(root, cfg, 'cutover_slow', f"legacy worker not drained after {int(waited)} s: jobs {d['jobs']} open {d['open']} state {d['state']}")
        return 'draining'
    if sys.platform == 'darwin' and shutil.which('launchctl'):
        plist = Path('~/Library/LaunchAgents').expanduser() / f'{label}.plist'
        backups = Path(root) / 'backups'
        backups.mkdir(exist_ok=True)
        if plist.exists():
            shutil.copy2(plist, backups / plist.name)
        rc = subprocess.run(['launchctl', 'bootout', f'gui/{os.getuid()}/{label}'], capture_output=True, text=True, check=False)
        log(f'auto-cutover: bootout {label} rc={rc.returncode} {rc.stderr.strip()[:120]}')
    if legacy_alive(cfg):
        log('auto-cutover: legacy worker still alive after bootout; waiting')
        return 'draining'
    from .hubctl import adopt_legacy
    conn = db.connect(root)
    report = adopt_legacy(conn, root, cfg, 'hub/actuator/auto-cutover')
    db.kv_set(conn, 'cutover', dict(at=db.now_iso(), by='auto', control=report.get('control'), frozen=report.get('frozen'), retired=report.get('retired')))
    db.event(conn, root, 'hub/actuator', 'auto_cutover_live', report)
    conn.close()
    state['mode'] = 'live'
    state.pop('cutover_pending', None)
    log(f"auto-cutover: live; control {report.get('control')} frozen {report.get('frozen')} retired {report.get('retired')}")
    notify(root, cfg, 'cutover', f"executor is LIVE (control {report.get('control')}); legacy worker unloaded, plist in {Path(root) / 'backups'}")
    return 'live'


def register_check(root, cfg, state, log):
    """Register candidates on request (`<mirror>/control/register.json`: {"candidates": [{"dir": "bots/x", "priority": 120}, ...]}).

    Each directory is frozen and registered exactly as `hubctl candidate register --from-dir` would (manifest validation,
    fingerprint de-duplication, archive byte-check); failures are reported per candidate in `register.done.json`, never
    fatal. Registration alone queues the candidate: preflight, upload, dev coverage and screening follow automatically.
    """
    ctl = Path(cfg['paths']['mirror']) / 'control'
    req = ctl / 'register.json'
    if not req.exists():
        return None
    from .candidates import register_from_dir
    repo = Path(cfg['paths']['repo'])
    try:
        body = json.loads(req.read_text())
    except ValueError:
        body = {'candidates': [], 'error': 'request is not JSON'}
    results = []
    conn = db.connect(root)
    for item in body.get('candidates') or []:
        if item.get('name') and not item.get('dir'):
            # re-prioritise an existing candidate (the director's queue order; evidence tier, never a local score)
            row = conn.execute('SELECT name, status, priority FROM candidates WHERE name=?', (item['name'],)).fetchone()
            if not row:
                results.append(dict(name=item['name'], error='unknown candidate'))
            elif item.get('priority') is None:
                results.append(dict(name=item['name'], error='priority required'))
            else:
                conn.execute('UPDATE candidates SET priority=?, updated_at=? WHERE name=?', (int(item['priority']), db.now_iso(), item['name']))
                db.event(conn, root, item.get('by') or body.get('by') or 'hub/actuator/register', 'candidate_prioritized', dict(name=item['name'], priority=int(item['priority']), was=row['priority'], reason=item.get('reason')))
                results.append(dict(name=item['name'], status=row['status'], priority=int(item['priority']), was=row['priority']))
            continue
        directory = repo / item.get('dir', '')
        try:
            row = register_from_dir(conn, root, directory, item.get('by') or body.get('by') or 'hub/actuator/register', priority=item.get('priority'))
            results.append(dict(dir=item.get('dir'), name=row['name'], status=row['status'], priority=row['priority'], fingerprint=row['fingerprint'][:12]))
        except Exception as exc:
            results.append(dict(dir=item.get('dir'), error=f'{type(exc).__name__}: {str(exc)[:300]}'))
    db.event(conn, root, 'hub/actuator', 'register_request', dict(note=body.get('note'), results=results))
    conn.close()
    out = dict(at=db.now_iso(), note=body.get('note'), results=results, error=body.get('error'))
    (ctl / 'register.done.json').write_text(json.dumps(out, indent=1, default=str))
    req.unlink(missing_ok=True)
    log(f"register request: {[(r.get('name') or r.get('dir'), r.get('status') or r.get('error', '')[:60]) for r in results]}")
    notify(root, cfg, 'register', '; '.join(f"{r.get('name') or r.get('dir')}: {r.get('status') or r.get('error', '')[:80]}" for r in results)[:400])
    return out


def restore_check(root, cfg, state, client, log):
    """Director-requested restore (`<mirror>/control/restore.json`: {"previous": id, "candidate": id, "reason": …}).

    Only re-activates `previous` when `candidate` is what is active now and `candidate` is an executor upload or the
    request says `force: true` (a director decision recorded by name); sets the control to `previous`. Answers in
    `restore.done.json`. This exists for the case the automatic repair cannot decide (28 Sep 15:08 UTC).
    """
    ctl = Path(cfg['paths']['mirror']) / 'control'
    req = ctl / 'restore.json'
    if not req.exists() or client is None:
        return None
    try:
        body = json.loads(req.read_text())
    except ValueError:
        body = {}
    conn = db.connect(root)
    out = dict(at=db.now_iso(), request=body)
    try:
        subs = client.get('/api/v1/submissions')
        active = [s for s in subs if s.get('status') == 'active']
        active_id = active[0]['id'] if len(active) == 1 else None
        names = {s.get('id'): s.get('name') or '' for s in subs}
        prev, cand = body.get('previous'), body.get('candidate')
        if active_id != cand:
            out['result'] = f'refused: active is {active_id}, not the named candidate {cand}'
        elif not (names.get(cand, '').endswith('-ai') or body.get('force')):
            out['result'] = f'refused: {cand} ({names.get(cand)}) is not an executor upload; pass force: true with a reason to override a teammate choice'
        elif prev not in names:
            out['result'] = f'refused: previous {prev} is not a known submission'
        else:
            hub_executor.mutate(conn, client, 'restore', f'/api/v1/submissions/{prev}/activate', {}, body.get('reason') or 'director restore', dict(submission=prev, candidate=cand, by=body.get('by')))
            hub_executor.set_control(conn, root, body.get('by') or 'director', prev, 'director', body.get('reason') or 'director restore')
            db.event(conn, root, body.get('by') or 'director', 'director_restore', dict(previous=prev, candidate=cand, reason=body.get('reason')))
            out['result'] = f'restored {prev} ({names.get(prev)}); control set'
    except Exception as exc:
        out['result'] = f'error: {type(exc).__name__}: {str(exc)[:200]}'
    conn.close()
    (ctl / 'restore.done.json').write_text(json.dumps(out, indent=1, default=str))
    req.unlink(missing_ok=True)
    log(f"restore request: {out['result']}")
    notify(root, cfg, 'restore', out['result'][:300])
    return out


def git_check(root, cfg, state, log):
    """Director-requested git pass (`<mirror>/control/git.json`: {"by": …, "note": …, "quiet_minutes": 0}) — the keeper's
    ordinary policy (include/never lists, merge origin, stop on conflict, push), run now instead of at the 3-hourly tick."""
    ctl = Path(cfg['paths']['mirror']) / 'control'
    req = ctl / 'git.json'
    if not req.exists():
        return None
    try:
        body = json.loads(req.read_text())
    except ValueError:
        body = {}
    policy = dict(cfg['git'])
    if body.get('quiet_minutes') is not None:
        policy['quiet_minutes'] = int(body['quiet_minutes'])
    merged_branches = []
    try:
        # optional: merge local work branches (the C1 worktree branches, e.g. cx/f) into main before the ordinary pass.
        # A conflict aborts that merge and is reported; nothing else is touched.
        for branch in body.get('merge') or []:
            if not re.match(r'^[A-Za-z0-9._/-]{1,80}$', str(branch)):
                merged_branches.append(dict(branch=branch, error='bad branch name'))
                continue
            repo = cfg['paths']['repo']
            opts = ['-X', body['strategy_option']] if body.get('strategy_option') in ('ours', 'theirs') else []   # conflict hunks only; non-conflicting hunks merge normally
            res = subprocess.run(['git', '-C', repo, 'merge', '--no-ff', '--no-edit', *opts, '-m', f'Merge {branch} into main (director request)', str(branch)], capture_output=True, text=True, check=False, timeout=300)
            if res.returncode:
                subprocess.run(['git', '-C', repo, 'merge', '--abort'], capture_output=True, text=True, check=False, timeout=120)
                merged_branches.append(dict(branch=branch, error=(res.stderr or res.stdout)[-400:]))
            else:
                merged_branches.append(dict(branch=branch, merged=True))
        report = git_sync(cfg['paths']['repo'], root, policy, actor=body.get('by') or 'hub/actuator/git-request')
        out = dict(at=db.now_iso(), note=body.get('note'), quiet_minutes=policy['quiet_minutes'], merged_branches=merged_branches, report=report)
    except Exception as exc:
        out = dict(at=db.now_iso(), note=body.get('note'), error=f'{type(exc).__name__}: {str(exc)[:300]}')
    (ctl / 'git.done.json').write_text(json.dumps(out, indent=1, default=str))
    req.unlink(missing_ok=True)
    rep = out.get('report') or {}
    log(f"git request: committed {len(rep.get('committed', []))} skipped {len(rep.get('skipped', []))} merged {rep.get('merged')} pushed {rep.get('pushed')} errors {rep.get('errors')} attention {rep.get('attention')} {out.get('error') or ''}")
    return out


def mode_check(root, cfg, state, log):
    """Director-requested executor mode (`<mirror>/control/mode.json`: {"mode": "off|shadow|auto|live", "by": …, "note": …}).

    Writes `[executor] mode` into HUB/hub.toml (the same knob `hubctl executor set-mode` sets) and restarts the daemon so
    the new mode takes effect on the next serve. `shadow` keeps harvest, corpus, register and git running but posts
    nothing: no uploads, no game requests, no activations (D-031: teammates own the submission interface)."""
    ctl = Path(cfg['paths']['mirror']) / 'control'
    req = ctl / 'mode.json'
    if not req.exists():
        return None
    try:
        body = json.loads(req.read_text())
    except ValueError:
        body = {}
    mode = str(body.get('mode', '')).strip()
    if mode not in ('off', 'shadow', 'auto', 'live'):
        out = dict(at=db.now_iso(), note=body.get('note'), error=f'mode must be off|shadow|auto|live, got {mode!r}')
    else:
        from .config import set_mode
        set_mode(root, mode)
        conn = db.connect(root)
        db.event(conn, root, body.get('by') or 'hub/actuator/mode-request', 'set_mode', dict(mode=mode, previous=state.get('configured'), note=body.get('note')))
        conn.close()
        out = dict(at=db.now_iso(), note=body.get('note'), mode=mode, previous=state.get('configured'), restart=True)
        state['restart'] = f'set_mode {mode}'
    (ctl / 'mode.done.json').write_text(json.dumps(out, indent=1, default=str))
    req.unlink(missing_ok=True)
    log(f"mode request: {out.get('mode') or out.get('error')}")
    return out


GATE_TESTS = ['tests.test_hub_core', 'tests.test_hub_git', 'tests.test_hub_legacy_ops', 'tests.test_hub_executor', 'tests.test_hub_daemon', 'tests.test_hub_quota_filler', 'tests.test_hub_discord_bot', 'tests.test_hub_api']


def redeploy_check(root, cfg, state, log):
    """Self-redeploy on request (`<mirror>/control/redeploy.json`, written by the director from any session).

    Refused (with `redeploy.rejected.json`) when a listed file's sha256 differs from the request, or the gate tests
    fail; deferred while an intent or transaction is open. Otherwise: snapshot `tools/hub` into HUB/app/<sha>,
    relink `current`, write `redeploy.done.json`, and exit non-zero so launchd relaunches the daemon on the new code.
    """
    ctl = Path(cfg['paths']['mirror']) / 'control'
    req = ctl / 'redeploy.json'
    if not req.exists():
        return None
    repo = Path(cfg['paths']['repo'])
    py = cfg['paths']['python']

    def finish(name, body):
        (ctl / name).write_text(json.dumps(body, indent=1, default=str))
        req.unlink(missing_ok=True)
        conn = db.connect(root)
        db.event(conn, root, 'hub/actuator', 'redeploy_' + name.split('.')[1], body)
        conn.close()
        notify(root, cfg, 'redeploy', f"{name.split('.')[1]}: {body.get('reason') or body.get('sha')}")
        return body
    try:
        body = json.loads(req.read_text())
    except ValueError:
        return finish('redeploy.rejected.json', dict(reason='request is not JSON', at=db.now_iso()))
    for rel, digest in (body.get('expect') or {}).items():
        target = repo / rel
        actual = sha256_file(target) if target.exists() else None
        if actual != digest:
            return finish('redeploy.rejected.json', dict(reason=f'{rel}: sha256 {actual} != expected {digest}', at=db.now_iso(), note=body.get('note')))
    conn = db.connect(root)
    opens = len(hub_executor.open_intents(conn)) + len(hub_executor.open_txs(conn))
    conn.close()
    if opens:
        if time.time() - (state.get('redeploy_seen') or time.time()) > 1800:
            return finish('redeploy.rejected.json', dict(reason=f'{opens} open intents/transactions for 30 min', at=db.now_iso()))
        state.setdefault('redeploy_seen', time.time())
        log(f'redeploy deferred: {opens} open intents/transactions')
        return None
    env = dict(os.environ, JKS_HUB_FIXTURE=str(repo / 'build/hub-fixture'))
    try:
        res = subprocess.run([py, '-m', 'unittest', *GATE_TESTS], cwd=str(repo), env=env, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return finish('redeploy.rejected.json', dict(reason='gate tests timed out', at=db.now_iso()))
    if res.returncode:
        return finish('redeploy.rejected.json', dict(reason='gate tests failed', tail=(res.stderr or res.stdout)[-1500:], at=db.now_iso()))
    sha = subprocess.run(['git', '-C', str(repo), '--no-optional-locks', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, check=False).stdout.strip() or 'nogit'
    sha = f"{sha}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    dep = subprocess.run([py, '-m', 'tools.hub.hubctl', '--root', str(root), '--agent', 'hub/actuator/redeploy', 'deploy', '--sha', sha], cwd=str(repo), capture_output=True, text=True, check=False, timeout=120)
    if dep.returncode:
        return finish('redeploy.rejected.json', dict(reason='deploy failed', tail=(dep.stderr or dep.stdout)[-800:], at=db.now_iso()))
    body = finish('redeploy.done.json', dict(sha=sha, at=db.now_iso(), tests='ok', note=body.get('note'), files=sorted((body.get('expect') or {}).keys())))
    state['restart'] = f'redeploy {sha}'
    return body



def corpus_thread(root, cfg, state, client, log, stop):
    """The public-replay corpus runs continuously in its own thread (D-025): it shares the paced client with the
    executor (so the key's 120/min ceiling is never crossed), stops its pass whenever an executor cycle is running
    (the executor has the API to itself), and slows down when the server has answered 429."""
    c = cfg.get('corpus') or {}
    interval = float(c.get('interval_seconds', 5))
    log(f"corpus thread: interval {interval} s, per pass {c.get('per_cycle_downloads')} downloads / {c.get('per_cycle_seconds')} s, refresh {c.get('refresh_per_pass')} per pass, client spacing {getattr(client, 'min_interval', None)} s")
    while not stop.exists() and not state.get('restart'):
        if state.get('executor_busy'):
            time.sleep(0.5)
            continue
        try:
            report = hub_corpus.fetch_pass(root, cfg, client, log, should_yield=lambda: bool(state.get('executor_busy')))
            state['corpus_last'] = report
            state['corpus_passes'] = state.get('corpus_passes', 0) + 1
            throttled = (report or {}).get('throttled', 0) - state.get('corpus_throttle_seen', 0)
            if throttled > 0:
                state['corpus_throttle_seen'] = (report or {}).get('throttled', 0)
                state['corpus_backoff_until'] = time.time() + 600
                log(f'corpus: server answered 429 ({throttled} new); corpus slows to one pass per 5 min for 10 min')
        except Exception:
            log('corpus error\n' + traceback.format_exc())
        pause = 300 if time.time() < state.get('corpus_backoff_until', 0) else interval
        if (state.get('corpus_last') or {}).get('fetched', 0) == 0 and (state.get('corpus_last') or {}).get('note'):
            pause = max(pause, 120)   # nothing to fetch: do not hammer the listings
        deadline = time.time() + pause
        while time.time() < deadline and not stop.exists() and not state.get('restart'):
            time.sleep(min(1.0, max(0.05, deadline - time.time())))


def serve(root, cfg, log):
    root = Path(root)
    (root / 'control').mkdir(parents=True, exist_ok=True)
    stop = root / 'control' / 'stop'
    if stop.exists():
        stop.unlink()
    conn = db.connect(root)
    configured = cfg['executor']['mode']
    mode = configured
    token = take_lease(conn, root)
    if token is None:
        log('another hub daemon holds the executor lease; exiting (duplicate_controller)')
        conn.close()
        return
    if configured == 'auto':
        # shadow until the cutover has happened (kv 'cutover', set by auto_cutover or cleared by release-legacy)
        mode = 'live' if db.kv_get(conn, 'cutover') and not legacy_alive(cfg) else 'shadow'
    if mode == 'live' and legacy_alive(cfg):
        log('executor mode is live but the legacy worker is alive; running as shadow until it is stopped')
        mode = 'shadow'
    db.event(conn, root, 'hub/actuator', 'serve_start', dict(pid=os.getpid(), mode=mode, configured=configured))
    conn.close()
    client = None
    if mode in ('shadow', 'live'):
        try:
            client = executor_client(cfg)
        except Exception as exc:
            log(f'executor client unavailable ({exc}); observer mode only')
            mode = 'off'
    state = {'mode': mode, 'token': token, 'configured': configured}
    if client is not None and (cfg.get('corpus') or {}).get('enabled') and (cfg.get('corpus') or {}).get('threaded', True):
        state['corpus_thread'] = threading.Thread(target=corpus_thread, args=(root, cfg, state, client, log, stop), name='corpus', daemon=True)
        state['corpus_thread'].start()
    next_cycle = 0
    next_exec = 0
    next_git = time.time() + 600  # first git pass ten minutes after start
    while not stop.exists() and not state.get('restart'):
        now = time.time()
        try:
            register_check(root, cfg, state, log)
        except Exception:
            log('register error\n' + traceback.format_exc())
        try:
            restore_check(root, cfg, state, client, log)
        except Exception:
            log('restore error\n' + traceback.format_exc())
        try:
            git_check(root, cfg, state, log)
        except Exception:
            log('git request error\n' + traceback.format_exc())
        try:
            redeploy_check(root, cfg, state, log)
            if state.get('restart'):
                break
        except Exception:
            log('redeploy error\n' + traceback.format_exc())
        try:
            mode_check(root, cfg, state, log)
            if state.get('restart'):
                break
        except Exception:
            log('mode request error\n' + traceback.format_exc())
        if configured == 'auto' and state['mode'] == 'shadow' and client is not None and state.get('cutover_pending'):
            try:
                auto_cutover(root, cfg, state, log)
            except Exception:
                log('auto-cutover error\n' + traceback.format_exc())
        if cfg['git'].get('enabled') and now >= next_git:
            try:
                report = git_sync(cfg['paths']['repo'], root, cfg['git'], actor='hub/actuator')
                log(f"git: committed {len(report['committed'])} skipped {len(report['skipped'])} merged {report.get('merged')} pushed {report.get('pushed')} errors {report['errors']} attention {report['attention']}")
                if report['attention'] or report['errors']:
                    notify(root, cfg, 'git', '; '.join(report['attention'] + report['errors'])[:300])
            except Exception:
                log('git error\n' + traceback.format_exc())
            next_git = now + cfg['git']['interval_seconds']
        try:
            safety_loop_once(root, cfg, state, log)
        except Exception:
            log('safety loop error\n' + traceback.format_exc())
        write_health(root, cfg, state, dict(legacy_alive=legacy_alive(cfg), api_calls=getattr(client, 'calls', None), api_throttled=getattr(client, 'throttled', None)))
        if client is not None and now >= next_exec:
            state['executor_busy'] = True
            try:
                conn = db.connect(root)
                renew_lease(conn, token)
                live_ok = state['mode'] == 'live' and not legacy_alive(cfg)
                cycle_started = time.time()

                def progress(phase, detail=None, _mode='live' if live_ok else 'shadow'):
                    write_health(root, cfg, state, dict(executor_phase=phase, executor_detail=detail, executor_cycle_started=cycle_started, executor_mode=_mode))
                # Reload the external config for each executor cycle so quota
                # filler on/off changes take effect without restarting the
                # long-lived daemon. Other daemon settings retain their
                # startup semantics.
                cycle_cfg = load_config(root)
                summary = hub_executor.run_cycle(conn, root, cycle_cfg, client, mode='live' if live_ok else 'shadow', actor='hub/executor', progress=progress)
                conn.close()
                conn = db.connect(root)
                clean = not summary['stop'] and not [a for a in summary['attention'] if a['kind'] in ('snapshot_failed', 'upload_ambiguous', 'intent_ambiguous', 'restore_uncertain')]
                db.kv_set(conn, 'executor_shadow_clean', (db.kv_get(conn, 'executor_shadow_clean') or 0) + 1 if clean else 0)
                if configured == 'auto' and state['mode'] == 'shadow' and (db.kv_get(conn, 'executor_shadow_clean') or 0) >= cfg['executor'].get('auto_cutover_after', 3):
                    state['cutover_pending'] = True
                conn.close()
                log(f"executor[{'live' if live_ok else 'shadow'}] {summary.get('seconds')} s: active {summary.get('active')} control {summary.get('control')} dispatched {len(summary['dispatched'])} plan {len(summary['plan'])} harvest {summary.get('harvest')} verdicts {summary['verdicts']} stop {summary['stop']} attention {[a['kind'] for a in summary['attention']]}")
                write_health(root, cfg, state, dict(executor_phase='idle', executor_detail=None, executor_seconds=summary.get('seconds')))
                for a in summary['attention']:
                    key = a['kind'] + ':' + json.dumps(a, default=str)[:60]
                    if key != state.get('last_exec_' + a['kind']):
                        notify(root, cfg, 'executor_' + a['kind'], json.dumps(a, default=str)[:300])
                        state['last_exec_' + a['kind']] = key
                for v in summary['verdicts']:
                    notify(root, cfg, 'verdict', json.dumps(v, default=str)[:300])
                if summary['stop']:
                    notify(root, cfg, 'executor_stop', summary['stop'])
            except Exception:
                log('executor error\n' + traceback.format_exc())
            state['executor_busy'] = False
            next_exec = now + cfg['executor']['interval_seconds']
        try:
            spawn_preflight(root, cfg, state, log)
        except Exception:
            log('preflight spawn error\n' + traceback.format_exc())
        if client is not None and (cfg.get('corpus') or {}).get('enabled') and not state.get('corpus_thread') and now >= state.get('next_corpus', 0):
            try:
                write_health(root, cfg, state, dict(executor_phase='corpus', executor_detail='public replay corpus fetch'))
                report = hub_corpus.fetch_pass(root, cfg, client, log)
                state['corpus_last'] = report
                write_health(root, cfg, state, dict(executor_phase='idle', corpus_last=report))
            except Exception:
                log('corpus error\n' + traceback.format_exc())
            state['next_corpus'] = now + int((cfg.get('corpus') or {}).get('interval_seconds', 300))
        if now >= next_cycle:
            try:
                tick = run_cycle(root, cfg, actor='hub/actuator')
                kinds = sorted({a['kind'] for a in tick['attention']})
                log(f"cycle {tick['epoch']}: incumbent {tick.get('incumbent')} active {tick.get('active_submission')} matched {tick.get('restoration_matched')} queue {len(tick['queue'])} attention {kinds} packet {tick.get('packet', '-')}")
                for a in tick['attention']:
                    key = f"{a['kind']}:{json.dumps(a['detail'], default=str)[:80]}"
                    if a['kind'] in ('external_incumbent_change', 'shadow_disagreement', 'open_transaction', 'active_mismatch') and key != state.get('last_' + a['kind']):
                        notify(root, cfg, a['kind'], json.dumps(a['detail'], default=str)[:300])
                        state['last_' + a['kind']] = key
                if tick.get('packet'):
                    notify(root, cfg, 'review_packet', f"packet written: {tick['packet']}")
            except Exception:
                log('cycle error\n' + traceback.format_exc())
            next_cycle = now + cfg['cadence']['cycle_seconds']
        for _ in range(cfg['cadence']['safety_seconds']):
            if stop.exists():
                break
            time.sleep(1)
    conn = db.connect(root)
    db.event(conn, root, 'hub/actuator', 'serve_stop', dict(pid=os.getpid(), restart=state.get('restart')))
    conn.close()
    write_health(root, cfg, state, dict(stopped=True))
    if state.get('restart'):
        log(f"restarting for {state['restart']} (exit 3; launchd relaunches on the new snapshot)")
        sys.exit(3)
    log('stopped')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--serve', action='store_true')
    p.add_argument('--once', action='store_true', help='run one cycle and exit')
    p.add_argument('--packet', action='store_true', help='force a review packet')
    p.add_argument('--root', default=None)
    a = p.parse_args(argv)
    root = Path(a.root) if a.root else hub_root()
    cfg = load_config(root)
    (root / 'logs').mkdir(parents=True, exist_ok=True)

    def log(text):
        line = f'{datetime.now(timezone.utc).isoformat()} {text}'
        print(line, flush=True)
        RECENT.append(line[:400])
        if 'error' in text.lower() or 'traceback' in text.lower():
            RECENT_ERRORS.append(line[:600])
        with (root / 'logs' / 'actuator.log').open('a') as handle:
            handle.write(line + '\n')
    if a.serve:
        try:
            serve(root, cfg, log)
        except SystemExit:
            raise
        except BaseException as exc:  # a crash must leave its trace in the mirror before launchd relaunches us
            log('daemon crashed\n' + traceback.format_exc())
            write_health(root, cfg, dict(mode='crashed', configured=cfg['executor'].get('mode')), dict(crashed=repr(exc)[:300]))
            raise
        return 0
    tick = run_cycle(root, cfg, actor='hub/cli', force_packet=a.packet)
    print(json.dumps({k: tick[k] for k in ('at', 'incumbent', 'active_submission', 'restoration_matched', 'attention', 'packet') if k in tick}, indent=1, default=str))
    return 0


if __name__ == '__main__':
    sys.exit(main())
