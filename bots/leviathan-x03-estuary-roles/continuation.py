"""Bounded existence search, not an adversarial or guaranteed survival oracle.

Bodies are tail-first. Other occupancy is held fixed. Confirmed pearls are
consumed once and delay tail release. Unknown edges/budget exhaustion return
None rather than a fabricated trap proof. The caller owns the shared budget.
"""


def survives(body, neighbors, occupied, pearls, depth, budget):
    if depth <= 0:
        return True
    stack = [(tuple(body), frozenset(), 0)]
    visited = set()
    uncertain = False
    while stack:
        if budget[0] <= 0:
            return None
        b, eaten, turn = stack.pop()
        key = (b, eaten, turn)
        if key in visited:
            continue
        visited.add(key)
        budget[0] -= 1
        for nxt in neighbors(b[-1]):
            if nxt == -2:
                uncertain = True
                continue
            if nxt < 0 or nxt in occupied or nxt in b:
                continue  # collision occurs BEFORE the tail can move
            grows = nxt in pearls and nxt not in eaten
            child = b + (nxt,) if grows else b[1:] + (nxt,)
            if turn + 1 >= depth:
                return True
            stack.append((child, eaten | {nxt} if grows else eaten, turn + 1))
    return None if uncertain else False
