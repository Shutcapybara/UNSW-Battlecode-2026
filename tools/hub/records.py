"""Tasks, findings, decisions and review responses (Part B §4.4, §5.3)."""
import json
import re
import secrets
import time
from pathlib import Path

from . import db

FINDING_KINDS = {'observation', 'hypothesis', 'correction', 'design', 'decision', 'verdict_note'}
TASK_KINDS = {'research', 'local_panel', 'replay_study', 'calibration', 'implementation', 'review'}


def new_id(prefix):
    return f'{prefix}-{time.strftime("%Y%m%d")}-{secrets.token_hex(3)}'


def create_task(conn, root, actor, kind, title, spec, exclusive=False, priority=100, task_id=None):
    if kind not in TASK_KINDS:
        raise ValueError('task kind must be one of ' + ', '.join(sorted(TASK_KINDS)))
    for key in ('goal', 'deliverable', 'done_when'):
        if not spec.get(key):
            raise ValueError(f'task spec needs {key}')
    task_id = task_id or new_id('T')
    db.upsert(conn, 'tasks', dict(id=task_id, kind=kind, title=title, spec=spec, exclusive=int(bool(exclusive)), priority=priority,
                                  created_by=actor, status='open'), 'id')
    db.event(conn, root, actor, 'task_created', dict(id=task_id, kind=kind, title=title))
    return task_id


def claim_task(conn, root, actor, task_id, ttl_minutes=90):
    task = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
    if not task:
        raise ValueError(f'unknown task {task_id}')
    if task['status'] != 'open':
        raise ValueError(f'task {task_id} is {task["status"]}')
    now = time.time()
    conn.execute('BEGIN IMMEDIATE')
    try:
        live = [dict(r) for r in conn.execute('SELECT * FROM task_claims WHERE task_id=? AND expires>?', (task_id, now))]
        if task['exclusive'] and live:
            holder = live[0]['owner']
            raise ValueError(f'exclusive task {task_id} is held by {holder} until {time.strftime("%H:%M:%SZ", time.gmtime(live[0]["expires"]))}')
        token = secrets.token_hex(8)
        conn.execute('INSERT INTO task_claims(task_id,owner,token,claimed_at,expires) VALUES(?,?,?,?,?)', (task_id, actor, token, now, now + ttl_minutes * 60))
        conn.execute('COMMIT')
    except Exception:
        conn.execute('ROLLBACK')
        raise
    db.event(conn, root, actor, 'task_claimed', dict(id=task_id, token=token, ttl_minutes=ttl_minutes))
    return token


def complete_task(conn, root, actor, task_id, result_ref):
    conn.execute("UPDATE tasks SET status='done', result_ref=?, updated_at=? WHERE id=?", (result_ref, db.now_iso(), task_id))
    db.event(conn, root, actor, 'task_completed', dict(id=task_id, result_ref=result_ref))


FRONT = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)


def parse_front_matter(text):
    m = FRONT.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            value = value.strip()
            if value.startswith('[') and value.endswith(']'):
                try:
                    value = json.loads(value)
                except ValueError:
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
            meta[key.strip()] = value
    return meta, text[m.end():]


def publish_finding(conn, root, actor, kind, title, body, evidence_refs=None, task_id=None, supersedes=None, finding_id=None, body_path=None):
    if kind not in FINDING_KINDS:
        raise ValueError('finding kind must be one of ' + ', '.join(sorted(FINDING_KINDS)))
    if kind == 'correction' and not supersedes:
        raise ValueError('a correction must name what it supersedes')
    finding_id = finding_id or new_id('F')
    if conn.execute('SELECT 1 FROM findings WHERE id=?', (finding_id,)).fetchone():
        raise ValueError(f'finding {finding_id} exists (findings are append-only; publish a correction instead)')
    stored = Path(root) / 'findings' / f'{finding_id}.md'
    stored.parent.mkdir(parents=True, exist_ok=True)
    stored.write_text(body)
    db.upsert(conn, 'findings', dict(id=finding_id, at=db.now_iso(), author=actor, kind=kind, title=title, body_path=body_path or str(stored), body=body,
                                     evidence_refs=evidence_refs or [], task_id=task_id, supersedes=supersedes, status='published'), 'id')
    if supersedes:
        conn.execute("UPDATE findings SET status='superseded' WHERE id=?", (supersedes,))
    db.event(conn, root, actor, 'finding_published', dict(id=finding_id, kind=kind, title=title, supersedes=supersedes))
    return finding_id


def import_finding(conn, root, actor, path):
    text = Path(path).read_text()
    meta, body = parse_front_matter(text)
    for key in ('id', 'author', 'kind', 'title'):
        if not meta.get(key):
            raise ValueError(f'front matter needs {key}')
    return publish_finding(conn, root, meta['author'], meta['kind'], meta['title'], body, evidence_refs=meta.get('evidence'),
                           task_id=meta.get('task') or None, supersedes=meta.get('supersedes') or None, finding_id=meta['id'], body_path=str(path))


def record_decision(conn, root, actor, experiment_id, checkpoint, verdict, detail, protocol):
    conn.execute('INSERT INTO decisions(at,experiment_id,checkpoint,verdict,detail,protocol,source,created_at) VALUES(?,?,?,?,?,?,?,?)',
                 (db.now_iso(), experiment_id, checkpoint, verdict, db.j(detail), protocol, actor, db.now_iso()))
    db.event(conn, root, actor, 'decision', dict(experiment=experiment_id, checkpoint=checkpoint, verdict=verdict, protocol=protocol))


def review_respond(conn, root, actor, packet_epoch, body):
    conn.execute('INSERT INTO review_responses(at,packet_epoch,actor,body) VALUES(?,?,?,?)', (db.now_iso(), packet_epoch, actor, body))
    out = Path(root) / 'review' / f'response-{packet_epoch}.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body)
    db.event(conn, root, actor, 'review_response', dict(packet_epoch=packet_epoch, lines=body.count('\n') + 1))
    return str(out)
