from __future__ import annotations

from ..state.world import DIR, World

SUMMARY_TAG = 0xA9 << 56
DENSITY_TAG = 0xAF << 56


def summary(world: World) -> int:
    team_max = max([world.length, *world.friendly_sizes.values()])
    enemy_max = max((enemy.visible_size for enemy in world.enemies.values()), default=0)
    return (SUMMARY_TAG
            | ((world.round & 1023) << 46)
            | (min(team_max, 1023) << 36)
            | ((world.dragon_id & 65535) << 20)
            | (min(enemy_max, 1023) << 10))


def density(world: World) -> int:
    # Quantised local observation. The receiver-side spatial fusion remains a
    # deliberate next step; the timestamp makes safe time decay possible.
    features = world.features
    friendly = min(127, round(features.friendly_density_ewma * 4))
    enemy = min(127, round(features.enemy_density_ewma * 4))
    x, y = world.head % world.width, world.head // world.width
    return (DENSITY_TAG
            | ((world.round & 1023) << 46)
            | ((x & 63) << 40)
            | ((y & 63) << 34)
            | ((friendly & 127) << 27)
            | ((enemy & 127) << 20))


def messages(world: World) -> list[tuple[str, int]]:
    status, local_density = summary(world), density(world)
    return [(direction, local_density if (world.round + index) % 2 else status)
            for index, direction in enumerate(DIR)]

