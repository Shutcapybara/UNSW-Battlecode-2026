from __future__ import annotations

from collections import deque

from .decisions import Attack, Growth, MoveAside, Split, Survive
from ..core.model import Decision, Execution
from ..state.features import safety_score
from ..state.world import DIR, World


class Policy:
    """First applicable complex execution wins; fallback handles food/frontier."""

    def __init__(self) -> None:
        # Preserve Hunter's aggressive ordering: a valid strike is an exact
        # execution, while generic threat avoidance handles the remainder.
        self.rules = (Growth(), Attack(), Survive(), MoveAside(), Split())

    def choose(self, world: World) -> Decision:
        for rule in self.rules:
            decision = rule.evaluate(world)
            if decision is not None:
                return decision
        return self._forage_or_explore(world)

    @staticmethod
    def _forage_or_explore(world: World) -> Decision:
        distance = [-1] * len(world.tiles)
        first = [-1] * len(world.tiles)
        queue = deque([world.head])
        distance[world.head] = 0
        best_pearl = (-10**9, -1)
        best_frontier = (-10**9, -1)
        while queue:
            position = queue.popleft()
            if position != world.head:
                tile = world.tiles[position]
                frontier = 0
                for direction in range(4):
                    adjacent = world.pos(position % world.width + (0, 1, 0, -1)[direction],
                                         position // world.width + (-1, 0, 1, 0)[direction])
                    frontier += not world.tiles[adjacent].visible and tile.edges[direction] != "w"
                safe = safety_score(world, first[position]) if distance[position] == 1 else 0
                explore_score = (frontier * 10000 - distance[position] * 20
                                 - min(world.visits[position], 24) * 25 + safe)
                if explore_score > best_frontier[0]:
                    best_frontier = explore_score, position
                if tile.pearl:
                    pearl_score = -distance[position] * 100 - world.visits[position]
                    if pearl_score > best_pearl[0]:
                        best_pearl = pearl_score, position
            for offset in range(4):
                direction = (offset + world.dragon_id + world.round // 8) % 4
                target = world.destination(position, direction)
                if target < 0 or distance[target] >= 0:
                    continue
                distance[target] = distance[position] + 1
                first[target] = direction if position == world.head else first[position]
                queue.append(target)
        target = best_pearl[1] if best_pearl[1] >= 0 else best_frontier[1]
        if target >= 0:
            execution = Execution.FORAGE if best_pearl[1] >= 0 else Execution.EXPLORE
            return Decision(execution, "MOVE " + DIR[first[target]])
        moves = [(safety_score(world, direction), direction)
                 for direction in range(4)
                 if world.destination(world.head, direction) >= 0]
        if moves:
            return Decision(Execution.FALLBACK, "MOVE " + DIR[max(moves)[1]])
        if world.length >= 4 and world.units < world.limit:
            return Decision(Execution.SPLIT, "SPLIT 2")
        return Decision(Execution.FALLBACK, "MOVE N")

