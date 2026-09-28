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
                'toolkit_pin': '1.0.0', 'probe_fixtures': [[9, 'A'], [20, 'B']], 'probe_opponent': 'bots/sinbad-v07-divecap'},
    'ranked_exposure_guard': {'blackout_before_even_utc_hour_minutes': 8, 'blackout_after_even_utc_hour_minutes': 12},
    'legacy': {'keepalive': True, 'stale_seconds': 300, 'launchd_label': 'au.battlecode.jks-live-validation', 'auto_clear_per_hour': 3},
    'notify': {'osascript': True, 'url': ''},
    'panels': {'screen': [62, 45, 470], 'confirmation': [853, 241, 481, 473, 133, 30, 193, 262, 130, 306, 213, 157]},
    'executor': {'mode': 'shadow', 'interval_seconds': 600},   # off | shadow | live ; live requires the legacy worker to be stopped (cutover_mac.sh)
    'git': {'enabled': True, 'interval_seconds': 10800, 'branch': 'main', 'push': True, 'quiet_minutes': 60,
            'include': ['bots/*', 'docs/*', 'game_stats/runs/*.parquet', 'game_stats/imports/*.json', 'tools/*', 'tests/*', 'maps/*.map', 'benchmark.toml', 'comparison.toml', 'README.md', '.gitignore'],
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
