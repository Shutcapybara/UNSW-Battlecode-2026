from __future__ import annotations

from ..decision import DecisionRule
from ...core.model import Decision, Execution
from ...state.features import safety_score
from ...state.world import DIR, World


class MoveAside(DecisionRule):
    def __init__(self) -> None:
        super().__init__()
        self.fire_on(lambda world: world.asked_to_move)

    def choose(self, world: World) -> Decision | None:
        moves = [(safety_score(world, direction), direction)
                 for direction in range(4)
                 if world.destination(world.head, direction) >= 0]
        if not moves:
            return None
        return Decision(Execution.YIELD, "MOVE " + DIR[max(moves)[1]])

