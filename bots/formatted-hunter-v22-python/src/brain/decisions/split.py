from __future__ import annotations

from ..decision import DecisionRule
from ...core.config import SPLIT_STOP
from ...core.model import Decision, Execution
from ...state.world import World


class Split(DecisionRule):
    def __init__(self) -> None:
        super().__init__()
        self.require(lambda world: world.length >= 4)
        self.require(lambda world: world.units < world.limit)
        self.require(lambda world: world.round < SPLIT_STOP or world.units < 3)

    def choose(self, world: World) -> Decision:
        return Decision(Execution.SPLIT, "SPLIT 2")

