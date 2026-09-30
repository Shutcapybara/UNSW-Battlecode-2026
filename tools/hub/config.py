"""Hub root resolution and portable configuration (Part B §4.6)."""
import copy
import json
import os
import sys
from pathlib import Path

from .toml_lite import loads as toml_loads

DEFAULT_ROOT = '/Users/alik/Documents/Projects/battlecode-hub'
REPO_ROOT = Path(__file__).resolve().parents[2]
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
    # Opt-in automatic quota filler.  The normal candidate planner runs first;
    # the filler spends only the unused part of each rolling 60-game pool.
    'quota_filler': {'enabled': False, 'top_n': 10, 'batch_games': 10, 'cycle_games': 10,
                     'field_opponents': [], 'reserve_games': {}, 'include_ladder_devs': True},
    'runtime': {'local_gate': {'max_points': 80_000_000, 'p99_points': 60_000_000}, 'live_gate': {'max_points': 95_000_000},
                'toolkit_pin': '1.0.0', 'probe_fixtures': [[9, 'A'], [20, 'B'], [21, 'A'], [15, 'B']], 'probe_opponent': 'bots/sinbad-v07-divecap'},   # + Slithery Fight A, Trauma B (A1-Q6: yuna-v02 peaked 97.5 M on never-probed Slithery)
    'ranked_exposure_guard': {'blackout_before_even_utc_hour_minutes': 8, 'blackout_after_even_utc_hour_minutes': 12},
    'legacy': {'keepalive': True, 'stale_seconds': 300, 'launchd_label': 'au.battlecode.jks-live-validation', 'auto_clear_per_hour': 3},
    'notify': {'osascript': True, 'url': ''},
    # screen: 45 (band-like, share 0.54), 752 (dev test 2, rank 85, dev pool — no field quota), 62 (the elimination stress test);
    # 470 (rank 6, share 0.32) dropped per A1-Q5/Q2: both arms lose to it, so it yields few discordant pairs and no band information
    'panels': {'screen': [545, 752, 45], 'confirmation': [853, 241, 481, 473, 133, 30, 193, 262, 130, 306, 213, 157]},   # D-026: screen on the dev allowance (545 rank-15 swarm, 752 weak) + one field block (45) for calibration
    'executor': {'mode': 'auto', 'interval_seconds': 600, 'auto_cutover_after': 3, 'drain_timeout_seconds': 1800,
                 'snapshot_seconds': 240, 'harvest_seconds': 240},   # time budgets per cycle: a slow server shortens the work, never the safety
    # executor.mode: off | shadow | auto | live. 'auto' = shadow until `auto_cutover_after` consecutive clean cycles, then the daemon
    # itself stops the legacy worker, adopts its record and goes live (docs/hub/EXECUTOR_V2.md §Cutover). 'live' needs the
    # legacy worker stopped by hand (cutover_mac.sh). rollback_mac.sh sets 'off'.
    'corpus': {'enabled': True, 'dest': 'public_replays/corpus', 'per_team': 500, 'top_n': 50, 'band': [55, 85],   # S-1 stats assistant (lead, 30 Sep): top 50 collected   # D-028: targets deepened (history back past 28 Sep 14:40) 'per_cycle_seconds': 120, 'per_cycle_downloads': 120,
               'interval_seconds': 5, 'threaded': True, 'refresh_per_pass': 30,   # D-025: continuous, in its own thread, paced by the shared client (≈ 2 API calls per replay)
               # explicit teams: the current top (306 Cutlery, formerly Vibing++: whole history, decoy timeline), the screen/confirmation and dev opponents, the band teams that played us
               'teams': [{'id': 306, 'games': 3000, 'why': 'rank 1; suspected decoy submissions between autoscrims'}, {'id': 62, 'games': 6000, 'why': 'elimination specialist; HB-1 anatomy target (lead, 29 Sep): whole history'},
                         {'id': 545, 'games': 600, 'why': 'dev test 1 (swarm)'}, {'id': 470, 'games': 600, 'why': 'length racer'}, {'id': 45, 'games': 600, 'why': 'band-like screen opponent'},
                         {'id': 752, 'games': 300, 'why': 'dev test 2'}, {'id': 790, 'games': 300, 'why': 'band'}, {'id': 133, 'games': 300, 'why': 'band'}, {'id': 977, 'games': 300, 'why': 'band'},
                         {'id': 75, 'games': 300, 'why': 'band'}, {'id': 19, 'games': 300, 'why': 'band'}, {'id': 406, 'games': 300, 'why': 'band'}, {'id': 534, 'games': 300, 'why': 'band'},
                         {'id': 875, 'games': 300, 'why': 'band'}, {'id': 473, 'games': 300, 'why': 'band'}, {'id': 241, 'games': 300, 'why': 'band'}]},
    'git': {'enabled': True, 'interval_seconds': 10800, 'branch': 'main', 'push': True, 'quiet_minutes': 60,
            'include': ['bots/*', 'docs/*', 'game_stats/runs/*.parquet', 'game_stats/imports/*.json', 'game_stats/*.json', 'claude/*', 'tools/*', 'tests/*', 'maps/*.map', 'benchmark.toml', 'comparison.toml', 'comparison-*.toml', 'README.md', '.gitignore'],
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
    # The historical default is the Mac deployment path.  A checkout on
    # another host should remain usable without requiring an impossible
    # /Users/alik directory; hub-state/ is already the repository's ignored
    # local mirror/control surface.
    if sys.platform != 'darwin':
        return REPO_ROOT / 'hub-state'
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
    if sys.platform != 'darwin':
        # Normalize only the bundled Mac defaults.  Explicit local/remote
        # paths in hub.toml remain authoritative.
        paths = cfg['paths']
        if paths.get('repo') == DEFAULTS['paths']['repo']:
            paths['repo'] = str(REPO_ROOT)
        if paths.get('python') == DEFAULTS['paths']['python']:
            paths['python'] = sys.executable
        if paths.get('key_file') == DEFAULTS['paths']['key_file']:
            paths['key_file'] = str(REPO_ROOT / '.battlecode-api-key')
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
    defaults = copy.deepcopy(DEFAULTS)
    if sys.platform != 'darwin':
        defaults['paths']['repo'] = str(REPO_ROOT)
        defaults['paths']['python'] = sys.executable
        defaults['paths']['key_file'] = str(REPO_ROOT / '.battlecode-api-key')
    for section, values in defaults.items():
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


def set_quota_filler_enabled(root, enabled):
    """Toggle the automatic quota filler in the external hub config."""
    import re
    root = Path(root)
    path = root / 'hub.toml'
    if not path.exists():
        write_default_config(root)
    text = path.read_text()
    # Stop at the next TOML table header, not at an inline array such as
    # ``field_opponents = []`` inside this table.
    section = re.search(r'^\[quota_filler\][\s\S]*?(?=^\[[A-Za-z0-9_.-]+\]\s*$|\Z)', text, re.M)
    value = 'true' if enabled else 'false'
    if section:
        body = section.group(0)
        if re.search(r'^enabled\s*=', body, re.M):
            body2 = re.sub(r'^enabled\s*=.*$', f'enabled = {value}', body, count=1, flags=re.M)
        else:
            body2 = body.rstrip('\n') + f'\nenabled = {value}\n'
        text = text.replace(body, body2)
    else:
        text = text.rstrip('\n') + f'\n\n[quota_filler]\nenabled = {value}\n'
    path.write_text(text)
    return bool(enabled)


def set_quota_filler_reserve(root, games):
    """Set the same manual-test reserve for the field and dev pools."""
    import re
    games = max(0, int(games))
    root = Path(root)
    path = root / 'hub.toml'
    if not path.exists():
        write_default_config(root)
    text = path.read_text()
    # Stop at the next TOML table header, not at an inline array such as
    # ``field_opponents = []`` inside this table.
    section = re.search(r'^\[quota_filler\][\s\S]*?(?=^\[[A-Za-z0-9_.-]+\]\s*$|\Z)', text, re.M)
    value = f'{{field = {games}, dev = {games}}}'
    if section:
        body = section.group(0)
        if re.search(r'^reserve_games\s*=', body, re.M):
            body2 = re.sub(r'^reserve_games\s*=.*$', f'reserve_games = {value}', body, count=1, flags=re.M)
        else:
            body2 = body.rstrip('\n') + f'\nreserve_games = {value}\n'
        text = text.replace(body, body2)
    else:
        text = text.rstrip('\n') + f'\n\n[quota_filler]\nreserve_games = {value}\n'
    path.write_text(text)
    return {'field': games, 'dev': games}
