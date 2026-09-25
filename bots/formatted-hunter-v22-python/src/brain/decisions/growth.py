from __future__ import annotations

from ..decision import DecisionRule
from ...core.config import CROWN_START
from ...core.model import Decision, Execution
from ...state.world import DIR, World


class Growth(DecisionRule):
    def __init__(self) -> None:
        super().__init__()
        self.require(lambda world: world.round >= CROWN_START)
        self.require(lambda world: world.length >= max(world.friendly_sizes.values(), default=0))

    def choose(self, world: World) -> Decision | None:
        route = world.route(
            lambda position, distance: world.tiles[position].pearl or
            0 <= world.tiles[position].countdown < distance,
            world.enemy_reach(), 320)
        if route is None:
            return None
        return Decision(Execution.GROW, "MOVE " + DIR[route[0]])

