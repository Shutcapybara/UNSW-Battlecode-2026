"""Arrival-time target value; predictions never enter action simulation.

ETA is measured in single-step turns. The first step happens this round, so a
bed at route distance d is reached in round now+d-1. Countdown zero attempts
spawn before movement; occupied beds can fail to spawn. This is a destination
heuristic, never evidence that a sprint can pay for another step.
"""


def arrival_value(now, distance, due, pearl_value, ttl):
    """Length-valued target feature (V material / control).

    A future spawn qualifies only if strictly before route distance, matching
    hunter-v15's countdown < eta rule. Overdue predictions decay to zero;
    observing an empty tile replaces the old timer in sense().
    """
    if due > now + distance - 1:
        return 0.0
    overdue = max(0, now - due)
    if overdue > ttl:
        return 0.0
    return pearl_value * (1.0 - overdue / (ttl + 1.0))
