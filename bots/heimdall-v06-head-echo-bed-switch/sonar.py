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
    """Wait for only arrival-ready beds after a sonar head contact."""
    enemy_head = max(0, w.echo[4])
    return 0.0 if enemy_head else 12.0


def threat_multiplier():
    _kelp, _ally, _ally_head, enemy, enemy_head = w.echo
    activity = 0.025 * max(0, enemy) + 0.06 * max(0, enemy_head)
    return 1.0 + min(0.18, activity)
