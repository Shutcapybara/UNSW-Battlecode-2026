"""Ask the running hub daemon to redeploy itself from this checkout (runs anywhere the repository is mounted).

    python3 tools/hub/request_redeploy.py --note "why" [tools/hub/executor.py ...]

Writes `hub-state/control/redeploy.json` with the sha256 of each listed file (default: every file under tools/hub and
the hub gate test modules). The daemon (macOS) verifies the hashes against its own view of the checkout, runs the gate
tests, snapshots tools/hub into HUB/app/<sha>, relinks `current` and restarts itself; it answers with
`redeploy.done.json` or `redeploy.rejected.json` in the same directory. No hub root, database or API access needed.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE = ['tests/test_hub_core.py', 'tests/test_hub_git.py', 'tests/test_hub_legacy_ops.py', 'tests/test_hub_executor.py', 'tests/test_hub_daemon.py', 'tests/test_hub_quota_filler.py', 'tests/test_hub_discord_bot.py', 'tests/test_hub_api.py']


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--note', required=True)
    p.add_argument('--by', default='director')
    p.add_argument('files', nargs='*')
    a = p.parse_args(argv)
    files = a.files or [str(f.relative_to(REPO)) for f in sorted((REPO / 'tools/hub').rglob('*')) if f.is_file() and '__pycache__' not in f.parts] + GATE
    expect = {}
    for rel in files:
        path = REPO / rel
        if not path.exists():
            print(f'missing: {rel}', file=sys.stderr)
            return 2
        expect[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    ctl = REPO / 'hub-state' / 'control'
    ctl.mkdir(parents=True, exist_ok=True)
    for stale in ('redeploy.done.json', 'redeploy.rejected.json'):
        try:
            (ctl / stale).unlink(missing_ok=True)
        except OSError:
            pass   # a mounted checkout may forbid deletes; the daemon overwrites the answer file anyway
    body = dict(requested_at=datetime.now(timezone.utc).isoformat(), by=a.by, note=a.note, expect=expect)
    (ctl / 'redeploy.json').write_text(json.dumps(body, indent=1))
    print(f'requested: {len(expect)} files hashed -> {ctl / "redeploy.json"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
