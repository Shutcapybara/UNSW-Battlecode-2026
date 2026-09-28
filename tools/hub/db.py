"""SQLite hub: schema, connection, events (Part B §4.2, §5.1). WAL mode; short transactions."""
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS candidates(
  name TEXT PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL, code_fingerprint TEXT NOT NULL,
  archive_path TEXT, archive_sha256 TEXT, source_files TEXT, language TEXT, lineage TEXT, author TEXT,
  lineage_parent_name TEXT, lineage_parent_fingerprint TEXT, source_ref TEXT,
  hypothesis TEXT, mechanism TEXT, expected_change TEXT, activation_contract TEXT, local_evidence TEXT,
  priority INTEGER DEFAULT 100, status TEXT NOT NULL, retired_reason TEXT, submission_id INTEGER, upload_name TEXT,
  api_source_hash TEXT, legacy_name TEXT, legacy_status TEXT, legacy_parent_submission INTEGER, control_policy TEXT,
  registered_by TEXT, registered_at TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS submissions(id INTEGER PRIMARY KEY, name TEXT, source_hash TEXT, language TEXT, status TEXT,
  first_seen TEXT, last_seen TEXT, owner TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY, candidate_name TEXT, candidate_submission INTEGER,
  control_submission INTEGER, protocol TEXT NOT NULL, alpha REAL, screen_opponents TEXT, confirmation_opponents TEXT,
  map_ids TEXT, status TEXT NOT NULL, verdict TEXT, decision TEXT, frozen_reason TEXT, source_fingerprint TEXT,
  opened_at TEXT, closed_at TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS blocks(id TEXT PRIMARY KEY, experiment_id TEXT, phase TEXT, control_submission INTEGER,
  candidate_submission INTEGER, opponent_team INTEGER, map_ids TEXT, order_json TEXT, requests TEXT,
  fill_attempts INTEGER DEFAULT 0, excluded_reason TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, at REAL, pool TEXT, opponent_team INTEGER, submission INTEGER,
  map_ids TEXT, count INTEGER, status TEXT, game_ids TEXT, block_id TEXT, origin TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS games(game_id INTEGER PRIMARY KEY, series_id TEXT, requested_at TEXT, ranked INTEGER,
  pool TEXT, origin TEXT, own_submission INTEGER, opponent_team INTEGER, opponent_submission INTEGER, map_id INTEGER,
  map_name TEXT, map_hash TEXT, api_side TEXT, observed_side TEXT, seed TEXT, status TEXT, verified INTEGER, error TEXT,
  score REAL, longest_margin INTEGER, rounds INTEGER, reason TEXT, faults INTEGER, caught_errors INTEGER,
  cpu_max INTEGER, cpu_recorded INTEGER, turns INTEGER, execution_mode TEXT DEFAULT 'server', decoder_revision TEXT,
  schema_version INTEGER, replay_sha256 TEXT, decoded_sha256 TEXT, experiment_id TEXT, block_id TEXT, phase TEXT,
  cohort TEXT, stages TEXT, opponent_stages TEXT, stats TEXT, ingested_at TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS series(series_id TEXT PRIMARY KEY, payload TEXT, fetched_at TEXT);
CREATE TABLE IF NOT EXISTS probes(id TEXT PRIMARY KEY, candidate_name TEXT, fingerprint TEXT, map_id INTEGER, side TEXT,
  toolkit_version TEXT, toolkit_path TEXT, seed TEXT, opponent_fingerprint TEXT, map_sha256 TEXT, load_avg_1m REAL,
  turns INTEGER, metered INTEGER, faults INTEGER, caught_errors INTEGER, max_points INTEGER, p99_points INTEGER,
  passed INTEGER, error TEXT, replay_path TEXT, log_sha256 TEXT, at TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS contract_results(id TEXT PRIMARY KEY, candidate_name TEXT, fingerprint TEXT, kind TEXT,
  reference_fingerprint TEXT, detail TEXT, passed INTEGER, at TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, experiment_id TEXT, checkpoint TEXT,
  verdict TEXT, detail TEXT, protocol TEXT, source TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, kind TEXT, title TEXT, spec TEXT, exclusive INTEGER DEFAULT 0,
  priority INTEGER DEFAULT 100, created_by TEXT, status TEXT, result_ref TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS task_claims(task_id TEXT, owner TEXT, token TEXT, claimed_at REAL, expires REAL);
CREATE TABLE IF NOT EXISTS findings(id TEXT PRIMARY KEY, at TEXT, author TEXT, kind TEXT, title TEXT, body_path TEXT,
  body TEXT, evidence_refs TEXT, task_id TEXT, supersedes TEXT, status TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS calibration(id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, fingerprint TEXT,
  control_fingerprint TEXT, measure TEXT, local_panel TEXT, local_mode TEXT, local_toolkit TEXT, local_value REAL,
  local_n INTEGER, live_pool TEXT, live_value REAL, live_n INTEGER, disagreement REAL, note TEXT);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, actor TEXT, kind TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS legacy_events(legacy_key TEXT PRIMARY KEY, at TEXT, message TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS external_actions(id TEXT PRIMARY KEY, at TEXT, kind TEXT, submission INTEGER,
  previous INTEGER, requested_by TEXT, note TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS ranked_exposure(game_id INTEGER PRIMARY KEY, series_id TEXT, submission INTEGER,
  elo_change REAL, overlapped_activation TEXT, note TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS shadow_checks(id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, kind TEXT, subject TEXT,
  computed TEXT, legacy TEXT, agree INTEGER);
CREATE TABLE IF NOT EXISTS ticks(epoch INTEGER PRIMARY KEY, at TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS packets(epoch INTEGER PRIMARY KEY, at TEXT, path TEXT, lines INTEGER);
CREATE TABLE IF NOT EXISTS review_responses(id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, packet_epoch INTEGER,
  actor TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY, at REAL, kind TEXT, path TEXT, body_sha256 TEXT, description TEXT,
  status TEXT, resolved_at TEXT, resolution TEXT, lease_token TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS transactions(id TEXT PRIMARY KEY, kind TEXT, payload TEXT, opened_at TEXT, closed_at TEXT, outcome TEXT);
CREATE TABLE IF NOT EXISTS quota_blocks(pool TEXT PRIMARY KEY, until REAL, reason TEXT);
CREATE TABLE IF NOT EXISTS opponent_exclusions(team_id INTEGER PRIMARY KEY, until REAL, reason TEXT);
CREATE TABLE IF NOT EXISTS executor_lease(singleton INTEGER PRIMARY KEY CHECK(singleton=1), host TEXT, pid INTEGER,
  token TEXT, acquired_at REAL, expires_at REAL, heartbeat_at REAL);
"""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def connect(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(root / 'hub.sqlite'), timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=30000')
    conn.executescript(SCHEMA)
    return conn


def j(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def kv_get(conn, key, default=None):
    row = conn.execute('SELECT value FROM kv WHERE key=?', (key,)).fetchone()
    return json.loads(row['value']) if row else default


def kv_set(conn, key, value):
    conn.execute('INSERT INTO kv(key,value,updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at',
                 (key, j(value), now_iso()))


def event(conn, root, actor, kind, payload=None):
    """Append to the events table and to events.jsonl (append-only, human-readable)."""
    at = now_iso()
    conn.execute('INSERT INTO events(at,actor,kind,payload) VALUES(?,?,?,?)', (at, actor, kind, j(payload or {})))
    with (Path(root) / 'events.jsonl').open('a') as handle:
        handle.write(json.dumps(dict(at=at, actor=actor, kind=kind, payload=payload or {}), ensure_ascii=False, default=str) + '\n')


def ensure_column(conn, table, column, decl):
    """ALTER TABLE ADD COLUMN when missing (schema growth without migrations)."""
    if column not in {c[1] for c in conn.execute(f'PRAGMA table_info({table})')}:
        conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {decl}')


def upsert(conn, table, row, key):
    """INSERT OR REPLACE by primary key while preserving created_at."""
    row = dict(row)
    cols = [c[1] for c in conn.execute(f'PRAGMA table_info({table})')]
    if 'updated_at' in cols:
        row['updated_at'] = now_iso()
    if 'created_at' in cols:
        existing = conn.execute(f'SELECT created_at FROM {table} WHERE {key}=?', (row[key],)).fetchone()
        row['created_at'] = existing['created_at'] if existing and existing['created_at'] else now_iso()
    row = {k: (j(v) if isinstance(v, (dict, list)) else v) for k, v in row.items() if k in cols}
    names = ','.join(row)
    marks = ','.join('?' for _ in row)
    conn.execute(f'INSERT OR REPLACE INTO {table}({names}) VALUES({marks})', tuple(row.values()))


def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def loads_row(row, *json_fields):
    out = dict(row)
    for field in json_fields:
        if out.get(field) is not None and isinstance(out[field], str):
            try:
                out[field] = json.loads(out[field])
            except ValueError:
                pass
    return out


def epoch():
    return int(time.time())
