"""P0: score stable intentions. No geometry, routing, mutation or command choice."""


def score(c, f, feature_version=0):
    kind = c['kind']
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
