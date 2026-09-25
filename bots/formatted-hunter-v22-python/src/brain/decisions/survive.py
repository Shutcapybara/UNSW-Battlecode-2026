from __future__ import annotations

from ..decision import DecisionRule
from ...core.model import Decision, Execution
from ...state.features import safety_score
from ...state.world import DIR, World


class Survive(DecisionRule):
    def __init__(self) -> None:
        super().__init__()
        self.fire_on(lambda world: bool(world.enemy_reach()))

    def choose(self, world: World) -> Decision | None:
        moves = [(safety_score(world, direction), direction)
                 for direction in range(4)
                 if world.destination(world.head, direction) >= 0]
        if not moves:
            return None
        score, direction = max(moves)
        if score < 0 or world.destination(world.head, direction) in world.enemy_reach():
            return None
        return Decision(Execution.SURVIVE, "MOVE " + DIR[direction])

