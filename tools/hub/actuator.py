"""The hub daemon: 60 s safety loop + 600 s evidence/decision cycle, legacy keep-alive, notifications.

Observer mode only on day one: it never calls a mutating API endpoint. `HUB/control/stop` stops it gracefully.
Run: `python -m hub.actuator --serve` (deployed copy) or `python -m tools.hub.actuator --once --packet` (repo).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
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


def serve(root, cfg, log):
    root = Path(root)
    (root / 'control').mkdir(parents=True, exist_ok=True)
    stop = root / 'control' / 'stop'
    if stop.exists():
        stop.unlink()
    conn = db.connect(root)
    mode = cfg['executor']['mode']
    token = take_lease(conn, root)
    if token is None:
        log('another hub daemon holds the executor lease; exiting (duplicate_controller)')
        conn.close()
        return
    if mode == 'live' and legacy_alive(cfg):
        log('executor mode is live but the legacy worker is alive; running as shadow until it is stopped')
        mode = 'shadow'
    db.event(conn, root, 'hub/actuator', 'serve_start', dict(pid=os.getpid(), mode=mode))
    conn.close()
    client = None
    if mode in ('shadow', 'live'):
        try:
            client = executor_client(cfg)
        except Exception as exc:
            log(f'executor client unavailable ({exc}); observer mode only')
            mode = 'off'
    state = {'mode': mode, 'token': token}
    next_cycle = 0
    next_exec = 0
    next_git = time.time() + 600  # first git pass ten minutes after start
    while not stop.exists():
        now = time.time()
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
        if client is not None and now >= next_exec:
            try:
                conn = db.connect(root)
                renew_lease(conn, token)
                live_ok = state['mode'] == 'live' and not legacy_alive(cfg)
                summary = hub_executor.run_cycle(conn, root, cfg, client, mode='live' if live_ok else 'shadow', actor='hub/executor')
                conn.close()
                conn = db.connect(root)
                clean = not summary['stop'] and not [a for a in summary['attention'] if a['kind'] in ('snapshot_failed', 'upload_ambiguous', 'intent_ambiguous', 'restore_uncertain')]
                db.kv_set(conn, 'executor_shadow_clean', (db.kv_get(conn, 'executor_shadow_clean') or 0) + 1 if clean else 0)
                conn.close()
                log(f"executor[{'live' if live_ok else 'shadow'}]: active {summary.get('active')} control {summary.get('control')} dispatched {len(summary['dispatched'])} plan {len(summary['plan'])} verdicts {summary['verdicts']} stop {summary['stop']} attention {[a['kind'] for a in summary['attention']]}")
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
            next_exec = now + cfg['executor']['interval_seconds']
        try:
            spawn_preflight(root, cfg, state, log)
        except Exception:
            log('preflight spawn error\n' + traceback.format_exc())
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
    db.event(conn, root, 'hub/actuator', 'serve_stop', dict(pid=os.getpid()))
    conn.close()
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
        with (root / 'logs' / 'actuator.log').open('a') as handle:
            handle.write(line + '\n')
    if a.serve:
        serve(root, cfg, log)
        return 0
    tick = run_cycle(root, cfg, actor='hub/cli', force_packet=a.packet)
    print(json.dumps({k: tick[k] for k in ('at', 'incumbent', 'active_submission', 'restoration_matched', 'attention', 'packet') if k in tick}, indent=1, default=str))
    return 0


if __name__ == '__main__':
    sys.exit(main())
