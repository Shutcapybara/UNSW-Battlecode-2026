"""Operations on the legacy live-validation worker, performed by the hub daemon on the Mac (D-009 watchdog).

- classify the reason of a `needs_review` stop as transient (auto-clearable when no transaction is open) or not;
- clear a review exactly as `runner.py --clear-review` does (archive the alert, remove it, request a plan);
- restart the worker through launchd (`kickstart -k`) between jobs, on request (`state/runner.restart`) or when its
  status is stale.
Everything is logged to `HUB/legacy_ops.jsonl`; auto-clears are capped per rolling hour.
"""
import calendar
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

TRANSIENT = re.compile(r"(HTTP 5\d\d|status 5\d\d|transport:|URLError|timed out|Timeout|Connection reset|Remote end closed|RemoteDisconnected|"
                       r"KeyError|TypeError|IndexError|JSONDecodeError|incomplete API payload|harvest error|transient class|Expected exactly one active submission)", re.I)
NEVER_AUTO = re.compile(r"(reconcil|Unacknowledged|duplicate|wrong team|DEV classification|Map roster|Decision rules|Pending upload|upload|switch|intent|activation)", re.I)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def last_error(log_path):
    """The last 'Cycle stopped' error text (or traceback tail) from a controller log."""
    try:
        text = Path(log_path).read_text(errors='replace')
    except OSError:
        return ''
    stopped = [l for l in text.splitlines() if 'Cycle stopped' in l]
    if stopped:
        return stopped[-1][-400:]
    tail = text.strip().splitlines()[-3:] if text.strip() else []
    return ' | '.join(tail)[-400:]


def classify(live, status):
    """Return (transient: bool, reason, error_text, open_tx: bool)."""
    live = Path(live)
    attention = status.get('attention') or {}
    reason = attention.get('reason') or ''
    error = last_error(attention.get('log', '')) if attention.get('log') else ''
    state = read_json(live / 'state/state.json', {}) or {}
    open_tx = any(state.get(k) for k in ('upload', 'switch', 'intent'))
    text = reason + ' ' + error
    transient = bool(TRANSIENT.search(text)) and not NEVER_AUTO.search(error or '') and 'preflight' not in reason
    if open_tx:
        transient = False
    return transient, reason, error, open_tx


def clear_review(live, note):
    live = Path(live)
    alert = live / 'state/runner_attention.json'
    if not alert.exists():
        return False
    logs = live / 'state/runner_logs'
    logs.mkdir(exist_ok=True)
    stamp = time.time_ns()
    shutil.copy2(alert, logs / f'cleared-review-{stamp}.json')
    (logs / f'cleared-review-{stamp}-note.txt').write_text(note + '\n')
    alert.unlink()
    (live / 'state/runner.renew').touch()
    return True


def kickstart(label, kill=False):
    if sys.platform != 'darwin' or not shutil.which('launchctl'):
        return dict(rc=None, note='not macOS')
    target = f'gui/{os.getuid()}/{label}'
    args = ['launchctl', 'kickstart'] + (['-k'] if kill else []) + [target]
    result = subprocess.run(args, capture_output=True, text=True, timeout=30, check=False)
    return dict(rc=result.returncode, stderr=result.stderr.strip()[:200], args=' '.join(args))


def log(root, entry):
    entry = dict(at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **entry)
    with (Path(root) / 'legacy_ops.jsonl').open('a') as handle:
        handle.write(json.dumps(entry, default=str) + '\n')
    return entry


def recent_auto_clears(root, window=3600):
    path = Path(root) / 'legacy_ops.jsonl'
    if not path.exists():
        return 0
    cutoff = time.time() - window
    n = 0
    for line in path.read_text().splitlines()[-200:]:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get('action') == 'auto_clear' and calendar.timegm(time.strptime(e['at'], '%Y-%m-%dT%H:%M:%SZ')) >= cutoff:   # UTC stamp (mktime - timezone was off by the DST hour)
            n += 1
    return n


def watchdog(root, cfg, state, notify, logger):
    """Called from the 60 s safety loop. Returns a dict of actions taken (possibly empty)."""
    live = Path(cfg['paths']['legacy_live'])
    label = cfg['legacy']['launchd_label']
    out = {}
    status = read_json(live / 'state/runner_status.json', {}) or {}
    jobs = status.get('jobs') or {}
    # 1. restart request between jobs (new runner code), only when the worker is idle
    if (live / 'state/runner.restart').exists() and not jobs and status.get('state') != 'restarting':
        res = kickstart(label, kill=True)
        if res.get('rc') == 0:
            try:
                (live / 'state/runner.restart').unlink()
            except OSError:
                pass
        out['restart'] = log(root, dict(action='restart', **res))
        logger(f'legacy watchdog: restart {res}')
        notify('legacy_restart', f'legacy worker restarted by request ({res.get("rc")})')
        return out
    # 2. transient needs_review: auto-clear with a cap
    if status.get('state') == 'needs_review':
        transient, reason, error, open_tx = classify(live, status)
        key = (status.get('attention') or {}).get('at')
        if key != state.get('last_review_seen'):
            state['last_review_seen'] = key
            cap = cfg['legacy'].get('auto_clear_per_hour', 3)
            if transient and recent_auto_clears(root) < cap:
                clear_review(live, f'auto-cleared by the hub watchdog: transient class; reason={reason!r}; error={error[:200]!r}')
                out['auto_clear'] = log(root, dict(action='auto_clear', reason=reason, error=error[:300]))
                logger(f'legacy watchdog: auto-cleared review ({error[:120]})')
                notify('legacy_auto_clear', f'auto-cleared transient review: {error[:160]}')
            else:
                out['review'] = log(root, dict(action='review_needed', reason=reason, error=error[:300], open_transaction=open_tx, transient=transient))
                notify('legacy_needs_review', f"{'cap reached; ' if transient else ''}{reason} :: {error[:160]}")
    return out
