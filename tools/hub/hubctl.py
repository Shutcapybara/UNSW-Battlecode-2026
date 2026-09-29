"""hubctl: the agent interface to the hub (Part B §5.3). Every write records the actor (`--agent` or JKS_AGENT).

    python -m tools.hub.hubctl status [--json]
    python -m tools.hub.hubctl packet | cycle [--packet] | doctor | init | mirror
    python -m tools.hub.hubctl candidate register --from-dir bots/<name> [--priority N] [--stage-live]
    python -m tools.hub.hubctl candidate list | show NAME | stage-live NAME | retire NAME --reason R | prioritize NAME --priority N
    python -m tools.hub.hubctl task create --kind K --title T --spec spec.json [--exclusive] | list | claim ID | complete ID --result REF
    python -m tools.hub.hubctl finding publish --kind K --title T --body file.md [--evidence refs.json] [--task ID] [--supersedes ID]
    python -m tools.hub.hubctl finding import path.md | list
    python -m tools.hub.hubctl decisions [--experiment ID] | review packet | review respond --packet EPOCH --body file.md
    python -m tools.hub.hubctl deploy --sha SHA
    python -m tools.hub.hubctl git status | git sync [--dry-run]
    python -m tools.hub.hubctl legacy status | legacy restart | legacy clear-review --note TEXT
    python -m tools.hub.hubctl quota status | quota on | quota off
    python -m tools.hub.hubctl executor status | executor once --mode shadow|live | executor adopt-legacy | executor release-legacy | executor set-mode off|shadow|auto|live
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import db, records
from .candidates import register_from_dir, stage_live
from .config import hub_root, load_config, set_quota_filler_enabled, write_default_config
from .cycle import run_cycle, mirror
from .gitkeeper import classify, sync as git_sync
from . import legacy_ops
from . import executor as hub_executor


def out(obj, as_json):
    if as_json:
        print(json.dumps(obj, indent=1, default=str))
    elif isinstance(obj, str):
        print(obj)
    else:
        print(json.dumps(obj, indent=1, default=str))


def cmd_status(conn, root, cfg, a):
    tick = db.rows(conn, 'SELECT payload FROM ticks ORDER BY epoch DESC LIMIT 1')
    tick = json.loads(tick[0]['payload']) if tick else {}
    status = dict(at=tick.get('at'), incumbent=tick.get('incumbent'), incumbent_name=tick.get('incumbent_name'), active=tick.get('active_submission'),
                  restoration_matched=tick.get('restoration_matched'), legacy_worker=tick.get('legacy_worker'), quota=tick.get('quota'), attention=tick.get('attention'),
                  experiments=tick.get('experiments'), queue=[dict(name=c['name'], status=c['status'], legacy_priority=c['legacy_priority'], hub_score=c['hub_score'], submission=c.get('submission')) for c in tick.get('queue', [])],
                  plan=tick.get('plan'), open_tasks=tick.get('open_tasks'), packet=db.kv_get(conn, 'last_packet_epoch'),
                  quota_filler=dict(configured=bool((cfg.get('quota_filler') or {}).get('enabled', False)),
                                    last=(db.kv_get(conn, 'executor_last', {}) or {}).get('quota_filler')))
    if a.json:
        out(status, True)
        return
    print(f"as of {status['at']}  incumbent {status['incumbent']} ({status['incumbent_name']})  active {status['active']}  matched {status['restoration_matched']}")
    w = status.get('legacy_worker') or {}
    print(f"legacy worker: {w.get('state')} age {w.get('age_seconds')}s jobs {w.get('jobs')} attention {w.get('attention')}")
    print(f"quota: {status.get('quota')}")
    print(f"quota filler: {status['quota_filler']['configured']} last={status['quota_filler']['last']}")
    print('attention: ' + (', '.join(a['kind'] for a in status.get('attention') or []) or 'none'))
    for e in status.get('experiments') or []:
        print(f"experiment {e['id'][:8]} {e['candidate']} vs {e['control']} {e['status']} [{e['protocol']}] screen {e['complete_blocks']['screen']}/3 net {e['screen_net']:+.0f} confirm {e['complete_blocks']['confirm']}/12 recorded={e['recorded_verdict']} computed={e['computed_verdict']}")
    for c in status['queue']:
        print(f"  {c['name']:40s} {c['status']:14s} prio {c['legacy_priority']} score {c['hub_score']} sub {c['submission']}")
    pl = status.get('plan') or {}
    print(f"plan: incumbent {pl.get('incumbent')} tasks {[t['kind'] + ':' + str(t['candidate']) for t in pl.get('tasks', [])]}")


def cmd_candidate(conn, root, cfg, a):
    if a.sub == 'register':
        row = register_from_dir(conn, root, a.from_dir, a.agent, priority=a.priority)
        out({k: row[k] for k in ('name', 'fingerprint', 'code_fingerprint', 'status', 'archive_path')}, a.json)
        if a.stage_live:
            out(stage_live(conn, root, cfg, row['name'], a.agent, priority=a.priority), a.json)
    elif a.sub == 'stage-live':
        out(stage_live(conn, root, cfg, a.name, a.agent, priority=a.priority), a.json)
    elif a.sub == 'list':
        rows_ = db.rows(conn, 'SELECT name, lineage, status, retired_reason, priority, submission_id, legacy_name, control_policy, registered_by FROM candidates ORDER BY priority DESC, name')
        out(rows_, a.json) if a.json else [print(f"{r['name']:42s} {r['lineage']:10s} {r['status']:14s} prio {r['priority']:4d} sub {r['submission_id']} {r['control_policy'] or ''} {r['retired_reason'] or ''}") for r in rows_]
    elif a.sub == 'show':
        row = conn.execute('SELECT * FROM candidates WHERE name=?', (a.name,)).fetchone()
        out(db.loads_row(row, 'source_files', 'activation_contract', 'local_evidence') if row else {'error': 'unknown'}, True)
    elif a.sub == 'retire':
        conn.execute("UPDATE candidates SET status='retired', retired_reason=?, updated_at=? WHERE name=?", (a.reason, db.now_iso(), a.name))
        db.event(conn, root, a.agent, 'candidate_retired', dict(name=a.name, reason=a.reason))
        out({'retired': a.name, 'reason': a.reason}, a.json)
    elif a.sub == 'prioritize':
        conn.execute('UPDATE candidates SET priority=?, updated_at=? WHERE name=?', (a.priority, db.now_iso(), a.name))
        db.event(conn, root, a.agent, 'candidate_prioritized', dict(name=a.name, priority=a.priority))
        out({'name': a.name, 'priority': a.priority}, a.json)


def cmd_quota(conn, root, cfg, a):
    enabled = bool((cfg.get('quota_filler') or {}).get('enabled', False))
    if a.sub == 'status':
        out(dict(enabled=enabled, settings=cfg.get('quota_filler') or {},
                 last=(db.kv_get(conn, 'executor_last', {}) or {}).get('quota_filler'),
                 quota=(db.kv_get(conn, 'executor_last', {}) or {}).get('quota')), a.json)
    else:
        enabled = a.sub == 'on'
        set_quota_filler_enabled(root, enabled)
        db.event(conn, root, a.agent, 'quota_filler_toggled', dict(enabled=enabled))
        out(dict(enabled=enabled, note='takes effect on the next executor cycle'), a.json)


def cmd_task(conn, root, cfg, a):
    if a.sub == 'create':
        spec = json.loads(Path(a.spec).read_text()) if a.spec else {}
        out({'id': records.create_task(conn, root, a.agent, a.kind, a.title, spec, exclusive=a.exclusive, priority=a.priority)}, a.json)
    elif a.sub == 'list':
        rows_ = [db.loads_row(t, 'spec') for t in db.rows(conn, "SELECT * FROM tasks WHERE status=? ORDER BY priority DESC, id", (a.status,))]
        out(rows_, a.json) if a.json else [print(f"{t['id']:22s} {t['kind']:14s} p{t['priority']:<4d} {t['title']}") for t in rows_]
    elif a.sub == 'claim':
        out({'token': records.claim_task(conn, root, a.agent, a.id, ttl_minutes=a.ttl)}, a.json)
    elif a.sub == 'complete':
        records.complete_task(conn, root, a.agent, a.id, a.result)
        out({'done': a.id}, a.json)


def cmd_finding(conn, root, cfg, a):
    if a.sub == 'publish':
        refs = json.loads(Path(a.evidence).read_text()) if a.evidence else []
        fid = records.publish_finding(conn, root, a.agent, a.kind, a.title, Path(a.body).read_text(), evidence_refs=refs, task_id=a.task, supersedes=a.supersedes)
        out({'id': fid}, a.json)
    elif a.sub == 'import':
        out({'id': records.import_finding(conn, root, a.agent, a.path)}, a.json)
    elif a.sub == 'list':
        rows_ = db.rows(conn, 'SELECT id, at, author, kind, title, status, supersedes FROM findings ORDER BY at DESC LIMIT 50')
        out(rows_, a.json) if a.json else [print(f"{f['id']:22s} {f['kind']:12s} {f['status']:10s} {f['title']} — {f['author']}") for f in rows_]


def cmd_decisions(conn, root, cfg, a):
    sql = 'SELECT id, at, experiment_id, checkpoint, verdict, protocol, source FROM decisions' + (' WHERE experiment_id=?' if a.experiment else '') + ' ORDER BY id'
    out(db.rows(conn, sql, (a.experiment,) if a.experiment else ()), True)


def cmd_review(conn, root, cfg, a):
    if a.sub == 'packet':
        path = Path(root) / 'review' / 'packet-latest.md'
        print(path.read_text() if path.exists() else 'no packet yet; run `hubctl cycle --packet`')
    elif a.sub == 'respond':
        out({'saved': records.review_respond(conn, root, a.agent, a.packet, Path(a.body).read_text())}, a.json)


def cmd_doctor(conn, root, cfg, a):
    report = dict(root=str(root), hub_sqlite=(Path(root) / 'hub.sqlite').exists(), python=sys.version.split()[0])
    for key, path in cfg['paths'].items():
        report[f'path.{key}'] = dict(path=path, exists=Path(path).exists()) if path else None
    tk = cfg['paths']['toolkit']
    if Path(tk).exists():
        try:
            report['toolkit_version'] = subprocess.check_output([tk, '--version'], text=True, timeout=20).strip().splitlines()[0]
        except Exception as exc:
            report['toolkit_version'] = repr(exc)
    live = Path(cfg['paths']['legacy_live'])
    report['legacy_runner_status'] = json.loads((live / 'state/runner_status.json').read_text()) if (live / 'state/runner_status.json').exists() else None
    report['launchd_legacy_loaded'] = None
    if sys.platform == 'darwin' and shutil.which('launchctl'):
        rc = subprocess.run(['launchctl', 'print', f"gui/{os.getuid()}/{cfg['legacy']['launchd_label']}"], capture_output=True, text=True, check=False)
        report['launchd_legacy_loaded'] = rc.returncode == 0
        rc = subprocess.run(['launchctl', 'print', f'gui/{os.getuid()}/au.battlecode.jks-hub'], capture_output=True, text=True, check=False)
        report['launchd_hub_loaded'] = rc.returncode == 0
    report['last_cycle_at'] = db.kv_get(conn, 'last_cycle_at')
    report['last_packet_epoch'] = db.kv_get(conn, 'last_packet_epoch')
    out(report, True)


def adopt_legacy(conn, root, cfg, actor):
    """Cutover step: freeze v1 experiments, retire legacy candidates the director did not re-queue, set the control."""
    from .legacy_import import read_json
    report = dict(frozen=[], retired=[], kept=[])
    for e in db.rows(conn, "SELECT id FROM experiments WHERE protocol='v1' AND status='running'"):
        conn.execute("UPDATE experiments SET status='superseded_by_cutover', frozen_reason='hub executor cutover', closed_at=?, updated_at=? WHERE id=?", (db.now_iso(), db.now_iso(), e['id']))
        report['frozen'].append(e['id'])
    rejected = {r['candidate_name'] for r in db.rows(conn, "SELECT candidate_name FROM experiments WHERE verdict LIKE 'reject%' AND candidate_name IS NOT NULL")}
    for c in db.rows(conn, "SELECT name, status, control_policy, legacy_name FROM candidates WHERE legacy_name IS NOT NULL"):
        if c['name'] in rejected:
            conn.execute("UPDATE candidates SET status='retired', retired_reason='strategy_lost_screen', updated_at=? WHERE name=?", (db.now_iso(), c['name']))
            report['retired'].append((c['name'], 'strategy_lost_screen'))
        elif c['status'] in ('uploaded', 'needs_runtime', 'dev_ok') and c['control_policy'] != 'current':
            conn.execute("UPDATE candidates SET status='retired', retired_reason='legacy_not_requeued', updated_at=? WHERE name=?", (db.now_iso(), c['name']))
            report['retired'].append((c['name'], 'legacy_not_requeued'))
        else:
            report['kept'].append((c['name'], c['status']))
    live = Path(cfg['paths']['legacy_live'])
    state = read_json(live / 'state/state.json', {}) or {}
    if db.kv_get(conn, 'control') is None and state.get('incumbent'):
        db.kv_set(conn, 'control', state['incumbent'])
        db.kv_set(conn, 'control_owner', 'legacy')
    report['control'] = db.kv_get(conn, 'control')
    db.kv_set(conn, 'legacy_adopted', dict(at=db.now_iso(), by=actor, frozen=report['frozen'], control=report['control']))   # the observer stops re-importing LIVE/state
    db.event(conn, root, actor, 'adopt_legacy', report)
    return report


def release_legacy(conn, root, actor):
    """Rollback step: let the observer import LIVE/state again (the legacy worker is being restarted)."""
    db.kv_set(conn, 'legacy_adopted', None)
    db.kv_set(conn, 'cutover', None)
    db.event(conn, root, actor, 'release_legacy', {})
    return dict(released=True)


def cmd_deploy(conn, root, cfg, a):
    """Copy this package into HUB/app/<sha>/hub and point HUB/app/current at it (the LaunchAgent runs the copy)."""
    src = Path(__file__).resolve().parent
    app = Path(root) / 'app'
    target = app / a.sha
    if target.exists():
        raise SystemExit(f'{target} exists; use a new sha')
    target.mkdir(parents=True)
    shutil.copytree(src, target / 'hub', ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))   # vendor/ included
    current = app / 'current'
    if current.is_symlink() or current.exists():
        current.unlink()
    current.symlink_to(target)
    db.event(conn, root, a.agent, 'deploy', dict(sha=a.sha, target=str(target)))
    out({'deployed': str(target), 'current': str(current)}, a.json)


def main(argv=None):
    p = argparse.ArgumentParser(prog='hubctl', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--json', action='store_true')
    p.add_argument('--root', default=None)
    p.add_argument('--agent', default=os.environ.get('JKS_AGENT', 'unknown/unknown/cli'))
    sp = p.add_subparsers(dest='cmd', required=True)
    sp.add_parser('status')
    sp.add_parser('init')
    sp.add_parser('doctor')
    sp.add_parser('mirror')
    c = sp.add_parser('cycle')
    c.add_argument('--packet', action='store_true')
    sp.add_parser('packet')
    cand = sp.add_parser('candidate').add_subparsers(dest='sub', required=True)
    r = cand.add_parser('register')
    r.add_argument('--from-dir', required=True)
    r.add_argument('--priority', type=int, default=None)
    r.add_argument('--stage-live', action='store_true')
    s = cand.add_parser('stage-live')
    s.add_argument('name')
    s.add_argument('--priority', type=int, default=None)
    cand.add_parser('list')
    cand.add_parser('show').add_argument('name')
    rt = cand.add_parser('retire')
    rt.add_argument('name')
    rt.add_argument('--reason', required=True)
    pr = cand.add_parser('prioritize')
    pr.add_argument('name')
    pr.add_argument('--priority', type=int, required=True)
    task = sp.add_parser('task').add_subparsers(dest='sub', required=True)
    tc = task.add_parser('create')
    tc.add_argument('--kind', required=True)
    tc.add_argument('--title', required=True)
    tc.add_argument('--spec', required=True)
    tc.add_argument('--exclusive', action='store_true')
    tc.add_argument('--priority', type=int, default=100)
    tl = task.add_parser('list')
    tl.add_argument('--status', default='open')
    tcl = task.add_parser('claim')
    tcl.add_argument('id')
    tcl.add_argument('--ttl', type=int, default=90)
    tco = task.add_parser('complete')
    tco.add_argument('id')
    tco.add_argument('--result', required=True)
    fnd = sp.add_parser('finding').add_subparsers(dest='sub', required=True)
    fp = fnd.add_parser('publish')
    fp.add_argument('--kind', required=True)
    fp.add_argument('--title', required=True)
    fp.add_argument('--body', required=True)
    fp.add_argument('--evidence')
    fp.add_argument('--task')
    fp.add_argument('--supersedes')
    fnd.add_parser('import').add_argument('path')
    fnd.add_parser('list')
    d = sp.add_parser('decisions')
    d.add_argument('--experiment')
    rv = sp.add_parser('review').add_subparsers(dest='sub', required=True)
    rv.add_parser('packet')
    rr = rv.add_parser('respond')
    rr.add_argument('--packet', type=int, required=True)
    rr.add_argument('--body', required=True)
    dp = sp.add_parser('deploy')
    dp.add_argument('--sha', required=True)
    lg = sp.add_parser('legacy').add_subparsers(dest='sub', required=True)
    lg.add_parser('status')
    lg.add_parser('restart')
    lc = lg.add_parser('clear-review')
    lc.add_argument('--note', required=True)
    quota = sp.add_parser('quota', help='toggle the automatic top-10/dev quota filler')
    qs = quota.add_subparsers(dest='sub', required=True)
    qs.add_parser('status')
    qs.add_parser('on')
    qs.add_parser('off')
    ex = sp.add_parser('executor').add_subparsers(dest='sub', required=True)
    ex.add_parser('status')
    eo = ex.add_parser('once')
    eo.add_argument('--mode', choices=['shadow', 'live'], default='shadow')
    ex.add_parser('adopt-legacy')
    ex.add_parser('release-legacy')
    ex.add_parser('set-mode').add_argument('mode', choices=['off', 'shadow', 'auto', 'live'])
    g = sp.add_parser('git').add_subparsers(dest='sub', required=True)
    g.add_parser('status')
    gs = g.add_parser('sync')
    gs.add_argument('--dry-run', action='store_true')
    a = p.parse_args(argv)
    root = Path(a.root) if a.root else hub_root()
    if a.cmd == 'init':
        write_default_config(root)
        conn = db.connect(root)
        db.event(conn, root, a.agent, 'init', dict(root=str(root)))
        conn.close()
        out({'root': str(root), 'config': str(root / 'hub.toml')}, a.json)
        return 0
    cfg = load_config(root)
    if a.cmd == 'cycle':
        tick = run_cycle(root, cfg, actor=a.agent, force_packet=a.packet)
        out({k: tick.get(k) for k in ('at', 'incumbent', 'active_submission', 'restoration_matched', 'attention', 'packet')}, True)
        return 0
    conn = db.connect(root)
    try:
        if a.cmd == 'status':
            cmd_status(conn, root, cfg, a)
        elif a.cmd == 'packet':
            a.sub = 'packet'
            cmd_review(conn, root, cfg, a)
        elif a.cmd == 'mirror':
            tick = db.rows(conn, 'SELECT payload FROM ticks ORDER BY epoch DESC LIMIT 1')
            out({'mirror': str(mirror(conn, root, cfg, json.loads(tick[0]['payload']) if tick else dict(at=db.now_iso(), attention=[], queue=[], retired=[], experiments=[], plan={}, legacy_worker={}, quota={})))}, a.json)
        elif a.cmd == 'candidate':
            cmd_candidate(conn, root, cfg, a)
        elif a.cmd == 'task':
            cmd_task(conn, root, cfg, a)
        elif a.cmd == 'finding':
            cmd_finding(conn, root, cfg, a)
        elif a.cmd == 'decisions':
            cmd_decisions(conn, root, cfg, a)
        elif a.cmd == 'review':
            cmd_review(conn, root, cfg, a)
        elif a.cmd == 'doctor':
            cmd_doctor(conn, root, cfg, a)
        elif a.cmd == 'deploy':
            cmd_deploy(conn, root, cfg, a)
        elif a.cmd == 'legacy':
            live = Path(cfg['paths']['legacy_live'])
            if a.sub == 'status':
                st = legacy_ops.read_json(live / 'state/runner_status.json', {}) or {}
                tr = legacy_ops.classify(live, st) if st.get('state') == 'needs_review' else None
                out(dict(runner=st, transient=tr), True)
            elif a.sub == 'restart':
                (live / 'state/runner.restart').touch()
                db.event(conn, root, a.agent, 'legacy_restart_requested', {})
                out({'requested': True, 'note': 'the runner (D-009) or the hub watchdog restarts it between jobs'}, a.json)
            elif a.sub == 'clear-review':
                ok = legacy_ops.clear_review(live, f'{a.agent}: {a.note}')
                db.event(conn, root, a.agent, 'legacy_review_cleared', dict(note=a.note, cleared=ok))
                out({'cleared': ok}, a.json)
        elif a.cmd == 'quota':
            cmd_quota(conn, root, cfg, a)
        elif a.cmd == 'executor':
            if a.sub == 'status':
                out(dict(mode=cfg['executor']['mode'], last=db.kv_get(conn, 'executor_last'), control=db.kv_get(conn, 'control'), control_owner=db.kv_get(conn, 'control_owner'),
                         probation=db.kv_get(conn, 'probation'), shadow_clean=db.kv_get(conn, 'executor_shadow_clean'), open_intents=hub_executor.open_intents(conn),
                         open_transactions=hub_executor.open_txs(conn), lease=db.rows(conn, 'SELECT host,pid,acquired_at,expires_at FROM executor_lease')), True)
            elif a.sub == 'once':
                from .api import Client
                if a.mode == 'live':
                    from .actuator import legacy_alive
                    if legacy_alive(cfg):
                        raise ValueError('the legacy worker is alive; stop it first (one live executor)')
                summary = hub_executor.run_cycle(conn, root, cfg, Client(cfg['paths']['repo']), mode=a.mode, actor=a.agent)
                out({k: v for k, v in summary.items() if k != 'plan'} | {'plan': summary['plan'][:20]}, True)
            elif a.sub == 'adopt-legacy':
                out(adopt_legacy(conn, root, cfg, a.agent), True)
            elif a.sub == 'release-legacy':
                out(release_legacy(conn, root, a.agent), True)
            elif a.sub == 'set-mode':
                from .config import set_mode
                db.event(conn, root, a.agent, 'set_mode', dict(mode=a.mode))
                out(dict(mode=set_mode(root, a.mode)), True)
        elif a.cmd == 'git':
            if a.sub == 'status':
                out(classify(cfg['paths']['repo'], cfg['git']), True)
            else:
                out(git_sync(cfg['paths']['repo'], root, cfg['git'], actor=a.agent, dry_run=a.dry_run), True)
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    finally:
        conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
