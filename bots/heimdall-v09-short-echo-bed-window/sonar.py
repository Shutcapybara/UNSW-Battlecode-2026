"""Low-cost use of aggregate protocol sonar echoes.

The echo contains counts for this dragon's previous-turn rays, not positions.
This module uses only enemy activity counts to modestly reweight a local head
threat that the visible world model has already identified. It never invents
a remote coordinate and never takes a sonar slot away from radio traffic.
"""
import world as w


def init():
    pass


def observe_echo():
    # Called immediately after world.sense(), which refreshes the tuple.
    return w.echo


def bed_wait():
    """Use a wide bed horizon in quiet lanes and shorten it after contact."""
    _kelp, _ally, _ally_head, enemy, enemy_head = w.echo
    activity = max(0, enemy) + 2 * max(0, enemy_head)
    return max(0.0, 6.0 - 3.0 * activity)


def threat_multiplier():
    _kelp, _ally, _ally_head, enemy, enemy_head = w.echo
    activity = 0.025 * max(0, enemy) + 0.06 * max(0, enemy_head)
    return 1.0 + min(0.18, activity)
