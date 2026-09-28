"""Hub root resolution and portable configuration (Part B §4.6)."""
import copy
import json
import os
from pathlib import Path

from .toml_lite import loads as toml_loads

DEFAULT_ROOT = '/Users/alik/Documents/Projects/battlecode-hub'
DEFAULTS = {
    'paths': {
        'repo': '/Users/alik/Documents/Projects/UNSW-Battlecode-2026',
        'python': '/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python',
        'toolkit': '/Users/alik/.local/bin/unswbc',
        'key_file': '/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.battlecode-api-key',
        'legacy_live': '/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation',
        'mirror': '',            # default: <repo>/hub-state
    },
    'team': {'id': 7, 'dev_opponents': [545, 752]},
    'cadence': {'safety_seconds': 60, 'cycle_seconds': 600, 'plan_horizon_seconds': 7200, 'review_every_seconds': 7200},
    'budget': {'hourly_games': {'field': 60, 'dev': 60}, 'executor_cap': {'field': 45, 'dev': 50}, 'harvest_per_cycle': 60},
    'runtime': {'local_gate': {'max_points': 80_000_000, 'p99_points': 60_000_000}, 'live_gate': {'max_points': 95_000_000},
                'toolkit_pin': '1.0.0', 'probe_fixtures': [[9, 'A'], [20, 'B'], [21, 'A'], [15, 'B']], 'probe_opponent': 'bots/sinbad-v07-divecap'},   # + Slithery Fight A, Trauma B (A1-Q6: yuna-v02 peaked 97.5 M on never-probed Slithery)
    'ranked_exposure_guard': {'blackout_before_even_utc_hour_minutes': 8, 'blackout_after_even_utc_hour_minutes': 12},
    'legacy': {'keepalive': True, 'stale_seconds': 300, 'launchd_label': 'au.battlecode.jks-live-validation', 'auto_clear_per_hour': 3},
    'notify': {'osascript': True, 'url': ''},
    # screen: 45 (band-like, share 0.54), 752 (dev test 2, rank 85, dev pool — no field quota), 62 (the elimination stress test);
    # 470 (rank 6, share 0.32) dropped per A1-Q5/Q2: both arms lose to it, so it yields few discordant pairs and no band information
    'panels': {'screen': [45, 752, 62], 'confirmation': [853, 241, 481, 473, 133, 30, 193, 262, 130, 306, 213, 157]},
    'executor': {'mode': 'auto', 'interval_seconds': 600, 'auto_cutover_after': 3, 'drain_timeout_seconds': 1800,
                 'snapshot_seconds': 240, 'harvest_seconds': 240},   # time budgets per cycle: a slow server shortens the work, never the safety
    # executor.mode: off | shadow | auto | live. 'auto' = shadow until `auto_cutover_after` consecutive clean cycles, then the daemon
    # itself stops the legacy worker, adopts its record and goes live (docs/hub/EXECUTOR_V2.md §Cutover). 'live' needs the
    # legacy worker stopped by hand (cutover_mac.sh). rollback_mac.sh sets 'off'.
    'corpus': {'enabled': True, 'dest': 'public_replays/corpus', 'per_team': 60, 'top_n': 30, 'band': [55, 85], 'per_cycle_seconds': 150, 'per_cycle_downloads': 40,
               # explicit teams: the current top (306 Cutlery, formerly Vibing++: whole history, decoy timeline), the screen/confirmation and dev opponents, the band teams that played us
               'teams': [{'id': 306, 'games': 400, 'why': 'rank 1; suspected decoy submissions between autoscrims'}, {'id': 62, 'games': 120, 'why': 'elimination specialist'},
                         {'id': 545, 'games': 120, 'why': 'dev test 1 (swarm)'}, {'id': 470, 'games': 120, 'why': 'length racer'}, {'id': 45, 'games': 120, 'why': 'band-like screen opponent'},
                         {'id': 752, 'games': 60, 'why': 'dev test 2'}, {'id': 790, 'games': 80, 'why': 'band'}, {'id': 133, 'games': 80, 'why': 'band'}, {'id': 977, 'games': 80, 'why': 'band'},
                         {'id': 75, 'games': 80, 'why': 'band'}, {'id': 19, 'games': 80, 'why': 'band'}, {'id': 406, 'games': 80, 'why': 'band'}, {'id': 534, 'games': 80, 'why': 'band'},
                         {'id': 875, 'games': 80, 'why': 'band'}, {'id': 473, 'games': 80, 'why': 'band'}, {'id': 241, 'games': 80, 'why': 'band'}]},
    'git': {'enabled': True, 'interval_seconds': 10800, 'branch': 'main', 'push': True, 'quiet_minutes': 60,
            'include': ['bots/*', 'docs/*', 'game_stats/runs/*.parquet', 'game_stats/imports/*.json', 'tools/*', 'tests/*', 'maps/*.map', 'benchmark.toml', 'comparison.toml', 'comparison-*.toml', 'README.md', '.gitignore'],
            'never': ['.battlecode-api-key', 'experiment_data/*', 'build/*', 'public_replays/*', 'hub-state/*', '*.replay', '*.replay.gz', 'game_stats.parquet', 'game_stats/sources/*', '*.tgz', '*.zip', '*.lock', '.venv/*', 'unswbc/*', 'replays/*', '*.log']},
}


def hub_root():
    env = os.environ.get('JKS_HUB_ROOT', '').strip()
    if env:
        return Path(env).expanduser()
    pointer = Path('~/.config/jkshub/root').expanduser()
    if pointer.exists():
        text = pointer.read_text().strip()
        if text:
            return Path(text).expanduser()
    return Path(DEFAULT_ROOT)


def _merge(base, override):
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(root=None):
    root = Path(root) if root else hub_root()
    cfg = copy.deepcopy(DEFAULTS)
    path = root / 'hub.toml'
    if path.exists():
        cfg = _merge(cfg, toml_loads(path.read_text()))
    cfg['root'] = str(root)
    if not cfg['paths'].get('mirror'):
        cfg['paths']['mirror'] = str(Path(cfg['paths']['repo']) / 'hub-state')
    # the git include/never lists in a hub.toml written by an earlier version are a floor, not a ceiling
    for key in ('include', 'never'):
        merged = list(cfg['git'].get(key) or [])
        merged += [x for x in DEFAULTS['git'][key] if x not in merged]
        cfg['git'][key] = merged
    return cfg


def write_default_config(root):
    """Write hub.toml with the defaults so operators can see and edit every knob."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / 'hub.toml'
    if path.exists():
        return path
    lines = ['# JKS hub configuration (Part B §4.6). Edit and restart the actuator.', '']
    for section, values in DEFAULTS.items():
        lines.append(f'[{section}]')
        for key, value in values.items():
            lines.append(f'{key} = {_toml_value(value)}')
        lines.append('')
    path.write_text('\n'.join(lines))
    return path


def _toml_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return '[' + ', '.join(_toml_value(v) for v in value) + ']'
    if isinstance(value, dict):
        return '{' + ', '.join(f'{k} = {_toml_value(v)}' for k, v in value.items()) + '}'
    raise TypeError(type(value))


def set_mode(root, mode):
    """Rewrite `[executor] mode` in hub.toml (appending the section when absent); used by the cutover/rollback scripts."""
    import re
    path = Path(root) / 'hub.toml'
    text = path.read_text() if path.exists() else ''
    if re.search(r'^\[executor\]', text, re.M):
        section = re.search(r'^\[executor\][^\[]*', text, re.M)
        body = section.group(0)
        if re.search(r'^mode\s*=', body, re.M):
            body2 = re.sub(r'^mode\s*=.*$', f'mode = "{mode}"', body, count=1, flags=re.M)
        else:
            body2 = body.rstrip('\n') + f'\nmode = "{mode}"\n'
        text = text.replace(body, body2)
    else:
        text = text.rstrip('\n') + f'\n\n[executor]\nmode = "{mode}"\n'
    path.write_text(text)
    return mode
