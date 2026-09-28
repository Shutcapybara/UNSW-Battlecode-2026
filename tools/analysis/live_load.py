"""Shared loader for the legacy live record (handoff A1, §2 row 1).

Reads `LIVE/state/state.json` with key-selecting code (never dumped whole) and returns flat
game rows annotated with their experiment block membership:

    game row = raw per-game dict + _block, _experiment, _phase, _arm ('candidate'|'control'|None)

Filters used by every analysis (handoff §3 standards): verified games only, origin/pool stated
per table, A-side only unless a B-side sample exists. Missing fields stay missing (None).

Usage:
    from live_load import load
    games = load()                       # verified only, all pools/origins
    field = [g for g in games if g['origin']=='controlled' and g['pool']=='field']
"""
import json
import os

STATE = os.environ.get(
    'JKS_LIVE_STATE',
    '/Users/alik/Documents/Codex/2026-09-27/your-prompt-is-in-the-markdown-2/outputs/live_validation/state/state.json')

STAGES = (100, 200, 250, 300, 320, 360, 380, 400, 450, 499)
COMPACT = {'Portals', 'Prisoners Dilemma', 'Devil', 'Trophy'}


def load(path=STATE, verified_only=True):
    with open(path) as f:
        d = json.load(f)
    block_of = {}
    for b in d.get('blocks', []):
        for req in b.get('requests') or []:
            for gid in req if isinstance(req, list) else []:
                block_of[int(gid)] = b
    games = []
    for gid, g in d['results'].items():
        if verified_only and not g.get('verified'):
            continue
        row = dict(g)
        row['game_id'] = int(gid)
        b = block_of.get(row['game_id'])
        row['_block'] = b['id'] if b else None
        row['_experiment'] = b.get('experiment') if b else None
        row['_phase'] = b.get('phase') if b else None
        row['_arm'] = None
        if b:
            if b.get('candidate') is not None and row.get('submission') == b['candidate']:
                row['_arm'] = 'candidate'
            elif b.get('control') is not None and row.get('submission') == b['control']:
                row['_arm'] = 'control'
        games.append(row)
    games.sort(key=lambda g: (g.get('requested') or '', g['game_id']))
    return games


def experiments(path=STATE):
    with open(path) as f:
        return json.load(f).get('experiments', [])


def stage(g, r, key, who='self'):
    src = g.get('stages') if who == 'self' else g.get('opponent_stages')
    try:
        return src[str(r)][key]
    except (KeyError, TypeError):
        return None


def per_1k(g, key, r=499, who='self'):
    v, t = stage(g, r, key, who), stage(g, r, 'turns', who)
    return 1000.0 * v / t if v is not None and t else None


def map_class(g):
    return 'compact' if g.get('map_name') in COMPACT else 'open'


def field_controlled(games):
    """The standard stratum: verified, controlled origin, field pool."""
    return [g for g in games if g.get('origin') == 'controlled' and g.get('pool') == 'field']
