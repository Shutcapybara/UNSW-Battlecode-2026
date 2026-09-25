from __future__ import annotations

from collections import deque

from ..decision import DecisionRule
from ...core.config import MIN_ATTACK_UNITS
from ...core.model import Decision, Execution
from ...state.world import DIR, World


class Attack(DecisionRule):
    def __init__(self) -> None:
        super().__init__()
        self.require(lambda world: world.units >= MIN_ATTACK_UNITS)

    def choose(self, world: World) -> Decision | None:
        paths = [""] * len(world.tiles)
        seen = {world.head}
        queue = deque([world.head])
        while queue:
            position = queue.popleft()
            if len(paths[position]) >= world.length - 1:
                continue
            for offset in range(4):
                direction = (offset + world.dragon_id + world.round) % 4
                target = world.destination(position, direction, False)
                if target < 0 or target in seen:
                    continue
                seen.add(target)
                paths[target] = paths[position] + DIR[direction]
                tile = world.tiles[target]
                if tile.enemy_head:
                    enemy = world.enemies.get(tile.dragon_id)
                    if enemy is not None and enemy.visible_size > world.length:
                        return Decision(Execution.ATTACK, "MOVE " + paths[target])
                    continue
                if not tile.occupied:
                    queue.append(target)
        return None

