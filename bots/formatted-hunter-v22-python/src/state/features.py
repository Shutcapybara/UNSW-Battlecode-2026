from __future__ import annotations

from collections import deque

from ..core import config
from ..core.model import LocalSafety
from .world import World


def local_safety(world: World, direction: int) -> LocalSafety:
    result = LocalSafety()
    start = world.destination(world.head, direction)
    if start < 0:
        return result
    danger = world.enemy_reach()
    seen = {start}
    queue = deque([start])
    while queue and result.reachable_tiles < config.LOCAL_SAFETY_CAP:
        position = queue.popleft()
        result.reachable_tiles += 1
        result.enemy_reachable_tiles += position in danger
        for next_direction in range(4):
            target = world.destination(position, next_direction)
            if target >= 0 and target != world.head and target not in seen:
                seen.add(target)
                queue.append(target)
    result.immediate_exits = sum(
        world.destination(start, candidate) >= 0
        and world.destination(start, candidate) != world.head
        for candidate in range(4)
    )
    result.dead_end = result.immediate_exits == 0
    return result


def safety_score(world: World, direction: int) -> int:
    value = local_safety(world, direction)
    return (value.reachable_tiles * config.SAFETY_REACHABLE_WEIGHT
            + value.immediate_exits * config.SAFETY_EXIT_WEIGHT
            - value.enemy_reachable_tiles * config.SAFETY_ENEMY_WEIGHT
            - value.dead_end * config.SAFETY_DEAD_END_PENALTY)

