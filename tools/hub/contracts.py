"""Activation contracts (Part B §7.3): did the mechanism act? Evaluated outcome-blind on probe logs/replays.

Implemented now: `trace_marker` (LOG ACT:<tag> lines in the verbose local log, counted per round window for the
candidate's own side) and `legacy_none` / `legacy_activity` (grandfathered). `behavioural_signature` and
`divergence_window` need the decoder statistics and command-stream comparison; until they exist a candidate that
declares them is recorded as `contract_unevaluated` and is not queued for a live screen by the hub.
"""
import re

HEADER = re.compile(r'^round (\d+): bot (\d+) \(team ([AB])\) stdout:\s*$')
POINTS = re.compile(r'^round (\d+): bot (\d+) \(team ([AB])\) points (\d+) memory (\d+)')


def parse_verbose_log(text):
    """Yield (round, bot, team, commands) for every turn block in a `unswbc run --verbose` log."""
    current = None
    commands = []
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            if current:
                yield (*current, commands)
            current = (int(m.group(1)), int(m.group(2)), m.group(3))
            commands = []
            continue
        if line.startswith('round ') and current:
            yield (*current, commands)
            current = None
            commands = []
            continue
        if current is not None:
            commands.append(line.rstrip())
    if current:
        yield (*current, commands)


def marker_counts(text, side):
    """Count LOG ACT:<tag> lines per (tag, round) for one side."""
    counts = {}
    for rnd, _bot, team, commands in parse_verbose_log(text):
        if team != side:
            continue
        for cmd in commands:
            if cmd.startswith('LOG ') and 'ACT:' in cmd:
                for tag in re.findall(r'ACT:[A-Za-z0-9_]+', cmd):
                    counts.setdefault(tag, {})
                    counts[tag][rnd] = counts[tag].get(rnd, 0) + 1
    return counts


def points_profile(text, side):
    points = [int(m.group(4)) for m in (POINTS.match(l) for l in text.splitlines()) if m and m.group(3) == side]
    if not points:
        return dict(turns=0, max_points=None, p99_points=None)
    values = sorted(points)
    return dict(turns=len(points), max_points=values[-1], p99_points=values[min(len(values) - 1, int(.99 * len(values)))])


def evaluate(contract, fixtures):
    """fixtures: list of dicts {label, side, log_text}. Returns dict(passed, kind, detail)."""
    kind = (contract or {}).get('kind', 'legacy_none')
    if kind in ('legacy_none', 'legacy_activity'):
        return dict(passed=True, kind=kind, detail={'note': 'grandfathered legacy candidate; not re-probed'})
    if kind == 'trace_marker':
        markers = contract.get('markers') or []
        if not markers:
            return dict(passed=False, kind=kind, detail={'error': 'trace_marker contract declares no markers'})
        per_marker = []
        for marker in markers:
            tag, lo, hi, minimum = (list(marker) + [1])[:4] if len(marker) >= 3 else (marker[0], 0, 501, 1)
            best = None
            for fx in fixtures:
                counts = marker_counts(fx['log_text'], fx['side']).get(tag, {})
                n = sum(v for r, v in counts.items() if int(lo) <= r < int(hi))
                if best is None or n > best['count']:
                    best = dict(fixture=fx.get('label'), count=n)
            per_marker.append(dict(tag=tag, lo=lo, hi=hi, minimum=minimum, best=best, satisfied=bool(best and best['count'] >= int(minimum))))
        return dict(passed=all(m['satisfied'] for m in per_marker) and bool(fixtures), kind=kind, detail={'markers': per_marker, 'fixtures': len(fixtures)})
    return dict(passed=None, kind=kind, detail={'error': f'contract kind {kind!r} is not evaluable yet (needs decoder statistics)'})
