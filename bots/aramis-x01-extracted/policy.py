"""Exact legacy maximum, with stable first-in tie breaking."""
def choose(actions):
    return max(actions, key=lambda pair: pair[0])
