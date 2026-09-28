#!/usr/bin/env python3
"""Queue experiment events in files and rebuild local aggregates later."""
from datetime import datetime, timezone
import argparse, hashlib, json, sqlite3, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "game_stats" / "local"

def now():
    return datetime.now(timezone.utc).isoformat()

def event_id(run_id, event_type, event_key):
    return hashlib.sha256(f"{run_id}\0{event_type}\0{event_key}".encode()).hexdigest()

class StatsStore:
    def __init__(self, root=DEFAULT_DIR, *, queue_only=False):
        self.root = Path(root).resolve()
        self.runs = self.root / "runs"
        self.runs.mkdir(parents=True, exist_ok=True)
        self.db = None
        if not queue_only:
            self.db = sqlite3.connect(self.root / "ledger.sqlite3")
            self.db.row_factory = sqlite3.Row
            self.db.executescript("""
            CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, started_at TEXT,
              producer TEXT, manifest_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY, run_id TEXT,
              event_type TEXT, event_key TEXT, created_at TEXT, payload_json TEXT,
              UNIQUE(run_id,event_type,event_key));
            CREATE INDEX IF NOT EXISTS event_type_idx ON events(event_type);
            """)

    def close(self):
        if self.db is not None:
            self.db.close()

    def start_run(self, *, producer, manifest, run_id=None):
        run_id = run_id or uuid.uuid4().hex
        run_dir = self.runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "manifest.json"
        if not path.exists():
            path.write_text(json.dumps({"run_id": run_id, "producer": producer,
                                        "started_at": manifest.get("created", now()),
                                        "manifest": manifest}, indent=2) + "\n")
        return run_id

    def append(self, run_id, event_type, event_key, payload):
        event = {"event_id": event_id(run_id, event_type, str(event_key)),
                 "run_id": run_id, "event_type": event_type,
                 "event_key": str(event_key), "created_at": now(), "payload": payload}
        with (self.runs / run_id / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        return event["event_id"]

    def append_match(self, run_id, event_key, payload):
        return self.append(run_id, "match_completed", event_key, payload)

    def rebuild_from_journals(self):
        if self.db is None:
            raise RuntimeError("rebuild requires a database-enabled store")
        self.db.execute("DELETE FROM events"); self.db.execute("DELETE FROM runs")
        seen = {}
        for run_dir in sorted(self.runs.iterdir()):
            if not run_dir.is_dir(): continue
            manifest_path = run_dir / "manifest.json"
            if manifest_path.exists():
                r = json.loads(manifest_path.read_text())
                self.db.execute("INSERT INTO runs VALUES(?,?,?,?)", (r["run_id"], r["started_at"], r["producer"], json.dumps(r["manifest"], sort_keys=True)))
            journal = run_dir / "events.jsonl"
            if not journal.exists(): continue
            for line in journal.read_text().splitlines():
                e = json.loads(line)
                if e["event_id"] in seen:
                    if seen[e["event_id"]]["payload"] != e["payload"]:
                        raise ValueError(f"conflicting event {e['event_id']}")
                    continue
                seen[e["event_id"]] = e
                self.db.execute("INSERT INTO events VALUES(?,?,?,?,?,?)", (e["event_id"], e["run_id"], e["event_type"], e["event_key"], e["created_at"], json.dumps(e["payload"], sort_keys=True)))
        self.db.commit()
        return len(seen)

    def standings(self):
        rows = self.db.execute("SELECT json_extract(payload_json,'$.bot_a') a, json_extract(payload_json,'$.bot_b') b, json_extract(payload_json,'$.team_a') ta, json_extract(payload_json,'$.team_b') tb, json_extract(payload_json,'$.outcome') outcome, json_extract(payload_json,'$.winner') winner FROM events WHERE event_type IN ('match_completed','match_error')")
        totals = {}
        for r in rows:
            a, b = r['a'] or r['ta'], r['b'] or r['tb']
            if not a or not b: continue
            for bot in (a, b): totals.setdefault(bot, {'bot':bot,'played':0,'wins':0,'draws':0,'losses':0,'errors':0,'points':0})
            if r['outcome'] == 'error': totals[a]['errors'] += 1; totals[b]['errors'] += 1
            elif r['outcome'] == 'draw':
                for bot in (a,b): totals[bot]['played'] += 1; totals[bot]['draws'] += 1; totals[bot]['points'] += 1
            else:
                winner = r['winner'] or (a if r['outcome'] == 'A' else b); loser = b if winner == a else a
                totals[winner]['played'] += 1; totals[winner]['wins'] += 1; totals[winner]['points'] += 3
                totals[loser]['played'] += 1; totals[loser]['losses'] += 1
        return sorted(totals.values(), key=lambda x: (-x['points'], -x['wins'], x['bot']))

def main():
    p = argparse.ArgumentParser(); p.add_argument('--root', type=Path, default=DEFAULT_DIR); p.add_argument('command', choices=['rebuild'])
    a = p.parse_args(); s = StatsStore(a.root)
    try: print(f"Imported {s.rebuild_from_journals()} events into {s.root / 'ledger.sqlite3'}")
    finally: s.close()
if __name__ == '__main__': main()
