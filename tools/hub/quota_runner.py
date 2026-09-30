"""One scheduled quota-filler cycle, without candidate uploads or activation.

Windows Task Scheduler invokes this every ten minutes. The shared executor
lease excludes another local controller; server history accounts for teammates.
"""
import argparse
import json
import os
import socket
import time
import uuid
from pathlib import Path

from . import db, executor
from .api import APIError, Client
from .config import hub_root, load_config


def acquire(conn):
    """Atomically claim a lease longer than the scheduled task's time limit."""
    now = time.time()
    conn.execute('BEGIN IMMEDIATE')
    try:
        row = conn.execute('SELECT * FROM executor_lease WHERE singleton=1').fetchone()
        if row and row['expires_at'] > now:
            conn.rollback()
            return None
        token = uuid.uuid4().hex
        conn.execute('INSERT OR REPLACE INTO executor_lease '
                     '(singleton,host,pid,token,acquired_at,expires_at,heartbeat_at) '
                     'VALUES(1,?,?,?,?,?,?)',
                     (socket.gethostname(), os.getpid(), token, now, now + 900, now))
        conn.commit()
        return token
    except Exception:
        conn.rollback()
        raise


class BattlesOnly:
    def __init__(self, client):
        self.client = client

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def post(self, path, body, content_type='application/json'):
        if path != '/api/v1/battles' or body.get('ranked') is not False:
            raise executor.Stop('quota runner permits only unranked battle requests')
        return self.client.post(path, body, content_type)


def run_cycle(conn, root, cfg, client, *, live=False, progress=None, now=None):
    now = time.time() if now is None else now
    executor.CLOCK['now'] = now
    executor.ensure_columns(conn)
    summary = dict(at=executor.now_iso(), mode='live' if live else 'shadow',
                   stop=None, attention=[], deferred=[], dispatched=[], plan=[],
                   reconciled=[], uploads=[])
    started = time.monotonic()
    client = BattlesOnly(client)
    try:
        if not cfg['quota_filler'].get('enabled'):
            summary['deferred'].append({'reason': 'quota_filler_disabled'})
            return summary
        if executor.open_txs(conn) or any(i['kind'] != 'battle' for i in executor.open_intents(conn)):
            raise executor.Stop('candidate executor has unfinished work; quota runner deferred')
        if conn.execute("SELECT 1 FROM experiments WHERE status='running' LIMIT 1").fetchone():
            raise executor.Stop('candidate experiment running; use its existing executor')
        snap = executor.Snapshot(client, conn, cfg, now, progress=progress)
        summary['active'] = snap.active
        # A truncated snapshot cannot establish that a lost acknowledgement
        # is absent. Preserve its reservation and wait for a complete snapshot.
        if not snap.history_incomplete:
            executor.reconcile(conn, root, cfg, snap, client, 'hub/quota-runner', summary)
        if executor.open_intents(conn):
            raise executor.Stop('waiting for uncertain battle requests to reconcile')
        db.kv_set(conn, 'control', snap.active)
        summary['control'] = snap.active
        summary['quota'] = executor.quota(conn, cfg, snap)
        if progress:
            progress('dispatch', None)
        executor.dispatch_quota_fill(conn, root, cfg, snap, client,
                                     'hub/quota-runner', summary['quota'], summary)
        if not live and summary.get('quota_filler'):
            summary['quota_filler']['dispatched_games'] = 0
    except (executor.Stop, APIError) as exc:
        summary['stop'] = str(exc)
    finally:
        executor.CLOCK['now'] = None
        summary['seconds'] = round(time.monotonic() - started, 1)
        db.kv_set(conn, 'executor_last', summary)
        db.event(conn, root, 'hub/quota-runner', 'quota_runner_cycle', summary)
    return summary


def health(root, **fields):
    body = dict(at=executor.now_iso(), pid=os.getpid(), **fields)
    path = root / 'quota-runner.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(body, indent=2), encoding='utf-8')
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='send bounded unranked requests')
    parser.add_argument('--root', type=Path, default=None)
    args = parser.parse_args()
    root = args.root or hub_root()
    cfg = load_config(root)
    conn = db.connect(root)
    token = acquire(conn)
    if not token:
        conn.close()
        print('Another executor holds the lease; skipping this cycle.', flush=True)
        return 0
    try:
        from .actuator import legacy_alive
        if legacy_alive(cfg):
            raise RuntimeError('legacy executor is running; quota runner deferred')
        def progress(phase, detail=None):
            health(root, phase=phase, detail=detail, mode='live' if args.live else 'shadow')
        progress('starting')
        result = run_cycle(conn, root, cfg, Client(cfg['paths']['repo']),
                           live=args.live, progress=progress)
        health(root, phase='waiting', last=result, interval_seconds=600,
               mode='live' if args.live else 'shadow')
        print(json.dumps(result, indent=2), flush=True)
        return 1 if result['stop'] else 0
    except Exception as exc:
        health(root, phase='error', error=str(exc))
        print(f'Quota runner failed: {exc}', flush=True)
        return 1
    finally:
        conn.execute('DELETE FROM executor_lease WHERE singleton=1 AND token=?', (token,))
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())
