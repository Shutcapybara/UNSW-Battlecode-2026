"""Versioned observation-only hazard features, shared by training and inference.

Raw row: steps, own post-action length, enemy visible length (+cut_extra),
truncated enemy flag, enemy ID later than own, round, own live unit count,
number of reaching enemy heads, map cells. No hidden replay truth enters X.
"""
FEATURE_VERSION = 1
NAMES = ("bias", "step2", "step3", "longer", "equal", "own_length", "enemy_length",
         "cut", "later_id", "round", "units", "multi_threat", "compact")


def vector(raw):
    steps, own, enemy, cut, later, rnd, units, count, cells = raw
    return (1.0, float(steps == 2), float(steps == 3), float(own > enemy),
            float(own == enemy), min(own, 30) / 10.0, min(enemy, 30) / 10.0,
            float(cut), float(later), rnd / 500.0, min(units, 32) / 16.0,
            float(count > 1), float(cells <= 625))


def bucket(raw):
    steps, own, enemy = raw[:3]
    relation = 2 if own > enemy else 1 if own == enemy else 0
    return (steps - 1) * 3 + relation


def prior(raw):
    steps, own, enemy = raw[:3]
    p = 0.9 if own > enemy else 0.7 if own == enemy else 0.1
    return p * (0.8 if steps > 1 else 1.0)
