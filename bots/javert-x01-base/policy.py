"""P0/P1/P3: score stable intentions. No geometry, routing, mutation or command choice."""
import settings
from params import P


def _saturated_hunt(f):
    """P3 gate: early-game population pressure makes space worth fighting for.

    True only when we are at the unit limit early, so ordinary mid/late games
    keep the inherited P1 scoring untouched. Enemy presence is not required
    here: the candidate itself names an enemy; this only prices the approach.
    """
    return bool(f.get('saturated') and f.get('phase_early'))


def score(c, f, feature_version=0):
    kind = c['kind']
    macro = c['params'].get('macro')
    if macro == 'advance': return 1.7 + 1.5 * c['params']['macro_gain']
    if macro == 'withdraw':
        return -0.5 + min(10.0, f['exposure']) + 3.0 * max(0.0, c['params']['balance'] + 0.3) + c['params']['protect']
    if kind == 'FEED_ALLY': return 100.0
    if kind == 'RETREAT': return -2.0 + min(10.0, f['exposure'])
    if kind == 'REPRODUCE':
        value = 4.0 - f['exposure']
        if settings.POLICY3:
            # P3: never mind extra bodies where there is no room to keep them.
            value -= P['w_confinement'] * max(0.0, 1.0 - f['openness'])
        return value
    if kind == 'ATTACK':
        if f['gain'] < 1: return -20.0
        value = 0.15 * min(40, f['gain']) * 0.93 ** f['distance']
        if settings.POLICY3 and _saturated_hunt(f) and f.get('len_balance', 0.0) > -0.5:
            # P3: at the unit cap early, pressuring enemies buys space for the
            # length we already hold; approach value is boosted, trades still
            # need their own explicit permission.
            value += P['w_space_hunt']
        if f['distance'] <= 3 and c['params']['visible']:
            base = 2.0 + f['gain'] - max(0, f['distance'] - 1)
            if settings.POLICY3 and _saturated_hunt(f) and f.get('len_balance', 0.0) > -0.5:
                base += P['w_space_hunt']
            return base
        return value
    if kind == 'SCOUT': return 0.12 * f['resource_value']
    value = 0.3 * f['resource_value']
    if feature_version == 1:
        # F1 changes only scoring of old remembered resource targets.
        value *= 0.5 ** (f['target_age'] / 12.0)
    return value


def rank(candidates, features, feature_version=0):
    return sorted(zip(candidates, features),
                  key=lambda pair: score(pair[0], pair[1], feature_version), reverse=True)


def rank_previews(candidates, facts, proposals, feature_version, round_number):
    """P1 consumes a frozen optional outcome preview; it never directs search.

    A nominated enemy is worth immediate trade gain only when the nominated
    executor can actually contact it. Chase uses a smaller, late-game score.
    All other P0 scores and F1 settings are held fixed.

    P3: while early and population-saturated, an approach-only ATTACK may be
    selected (raised cap) instead of being suppressed below the chase value.
    """
    ranked = []
    for c, f, proposal in zip(candidates, facts, proposals):
        value = score(c, f, feature_version)
        if proposal['command'] is None: value = -1e30
        elif c['kind'] == 'ATTACK' and proposal['outcome'] != 'intentional_head_trade':
            if settings.POLICY3 and _saturated_hunt(f):
                value = min(value, P['space_cap'])
            else:
                value = min(value, 0.8) if round_number >= 200 else -20.0
        ranked.append((value, c, proposal))
    return sorted(ranked, key=lambda row:row[0], reverse=True)
