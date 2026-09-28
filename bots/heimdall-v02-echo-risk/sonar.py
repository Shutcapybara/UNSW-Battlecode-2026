"""Turn-level use of the protocol's aggregate sonar echoes.

The game reports counts across all four rays but does not identify their
directions. Heimdall treats enemy hits as a weak global activity prior: it
raises the risk of blind portal exits and scales an already-local head-threat
estimate. It does not pretend the counts reveal a remote coordinate.
"""
import world as w


def init():
    pass


def observe_echo():
    # world.sense() refreshes this tuple every turn. Keeping the explicit hook
    # makes the observation/decision boundary visible in main.py.
    return w.echo


def _enemy_counts():
    _kelp, _ally, _ally_head, enemy, enemy_head = w.echo
    return max(0, enemy), max(0, enemy_head)


def adjust_exit_risk(base):
    bodies, heads = _enemy_counts()
    # A ray that found an enemy head is stronger evidence of a contested map
    # than one that merely touched a body. Keep this weak because there is no
    # location attached to the count.
    return min(1.0, base + min(0.22, 0.025 * bodies + 0.07 * heads))


def threat_multiplier():
    bodies, heads = _enemy_counts()
    return 1.0 + min(0.20, 0.015 * bodies + 0.04 * heads)
