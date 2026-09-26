"""P0: score stable intentions. No geometry, routing, mutation or command choice."""


def score(c, f, feature_version=0):
    kind = c['kind']
    macro = c['params'].get('macro')
    if macro == 'advance': return 1.7 + 1.5 * c['params']['macro_gain']
    if macro == 'withdraw':
        return -0.5 + min(10.0, f['exposure']) + 3.0 * max(0.0, c['params']['balance'] + 0.3) + c['params']['protect']
    if kind == 'FEED_ALLY': return 100.0
    if kind == 'RETREAT': return -2.0 + min(10.0, f['exposure'])
    if kind == 'REPRODUCE': return 4.0 - f['exposure']
    if kind == 'ATTACK':
        if f['gain'] < 1: return -20.0
        if f['distance'] <= 3 and c['params']['visible']:
            return 2.0 + f['gain'] - max(0, f['distance'] - 1)
        return 0.15 * min(40, f['gain']) * 0.93 ** f['distance']
    if kind == 'SCOUT': return 0.12 * f['resource_value']
    value = 0.3 * f['resource_value']
    if feature_version == 1:
        # F1 changes only scoring of old remembered resource targets.
        value *= 0.5 ** (f['target_age'] / 12.0)
    return value


def rank(candidates, features, feature_version=0):
    return sorted(zip(candidates, features),
                  key=lambda pair: score(pair[0], pair[1], feature_version), reverse=True)


def rank_previews(candidates, facts, proposals, feature_version, round_number, strategy_version=0):
    """P1 consumes a frozen optional outcome preview; it never directs search.

    A nominated enemy is worth immediate trade gain only when the nominated
    executor can actually contact it. Chase uses a smaller, late-game score.
    All other P0 scores and F1 settings are held fixed.
    """
    ranked = []
    for c, f, proposal in zip(candidates, facts, proposals):
        value = score(c, f, feature_version)
        if proposal['command'] is None: value = -1e30
        elif c['kind'] == 'ATTACK' and proposal['outcome'] != 'intentional_head_trade':
            value = min(value, 0.8) if round_number >= 200 else -20.0
        if strategy_version and proposal['command'] is not None:
            value = contextual_score(c, f, proposal, value)
        ranked.append((value, c, proposal))
    return sorted(ranked, key=lambda row:row[0], reverse=True)


def contextual_score(c, f, proposal, value):
    """DF1/DP1 changes scores only. No candidate/search/availability mutations.

    Counts, observed segments, observed area and global unit cap have distinct
    units. Area is a radius-four known lower bound; unknown room is not empty.
    These coefficients are hypotheses, not calibrated survival probabilities.
    """
    kind = c['kind']
    if kind == 'REPRODUCE':
        openness = min(1.0, f['known_area']/25.0)
        value = 4.0*openness - f['exposure'] - 5.0*max(0.0, f['congestion']-0.18)
        if f['free_exits'] <= 1: value -= 1.5
        if f['closed'] and f['free_cells'] < max(8, f['length']): value -= 8.0
        return value
    if kind == 'SCOUT':
        if f['portal_unknown']:
            return 1.8 * max(0.0, min(1.0, f['remaining']/160.0)) - 0.15*f['distance']
        if f['information']:
            return 0.8 + min(2.0, f['information']/16.0) * 0.93**f['distance'] \
                - 0.8*f['congestion'] - 0.5*max(0.0, -f['remote_balance'])
    if kind == 'ATTACK' and proposal['outcome'] != 'intentional_head_trade':
        saturation = max(0.0, min(1.0, (f['population_fraction']-0.75)/0.25))
        local_balance = (f['toward_ally_segments']-f['toward_enemy_segments']) \
            / max(1, f['toward_ally_segments']+f['toward_enemy_segments'])
        support = local_balance + 0.25*f['remote_balance']
        # Frontier means actual reachable enemy evidence, not a board heading.
        if f['gain'] >= 1 and f['length'] <= 5 and f['round'] < 350 \
                and f['direction_known'] and f['distance'] <= 8 and support >= -0.65:
            value = max(value, saturation*(3.5+min(2.0, f['gain']/8.0))
                        * 0.93**f['distance'] - 0.25*f['exposure'])
    return value
