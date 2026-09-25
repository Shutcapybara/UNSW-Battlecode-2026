from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TextIO

from ..core.config import EWMA_ALPHA
from ..core.model import EnemyMemory, MacroFeatures, Tile

DIR = "NESW"
DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)
MOVE_ASIDE = 1146242894


def _parts(stream: TextIO) -> list[str]:
    while line := stream.readline():
        values = line.partition("#")[0].split()
        if values:
            return values
    return []


def _field(stream: TextIO, expected: str) -> str | None:
    values = _parts(stream)
    if len(values) < 2 or values[0] != expected:
        return None
    return values[1]


@dataclass
class World:
    dragon_id: int
    team: str
    width: int
    height: int
    limit: int
    round: int = 0
    facing: int = 0
    length: int = 0
    units: int = 0
    head: int = 0
    asked_to_move: bool = False
    tiles: list[Tile] = field(default_factory=list)
    visits: list[int] = field(default_factory=list)
    known_edges: list[list[str]] = field(default_factory=list)
    known_edge: list[bool] = field(default_factory=list)
    known_pearls: dict[int, tuple[bool, int, int]] = field(default_factory=dict)
    enemies: dict[int, EnemyMemory] = field(default_factory=dict)
    friendly_sizes: dict[int, int] = field(default_factory=dict)
    features: MacroFeatures = field(default_factory=MacroFeatures)
    messages: list[int] = field(default_factory=list)

    @classmethod
    def read_initial(cls, stream: TextIO) -> "World | None":
        dragon_id = _field(stream, "ID")
        team = _field(stream, "TEAM")
        map_line = _parts(stream)
        limit = _field(stream, "UNIT_LIMIT")
        if dragon_id is None or team is None or limit is None or len(map_line) < 3 \
                or map_line[0] != "MAP":
            return None
        world = cls(int(dragon_id), team, int(map_line[1]), int(map_line[2]), int(limit))
        cells = world.width * world.height
        world.tiles = [Tile() for _ in range(cells)]
        world.visits = [0] * cells
        world.known_edges = [["."] * 4 for _ in range(cells)]
        world.known_edge = [False] * cells
        return world

    def pos(self, x: int, y: int) -> int:
        return (y % self.height) * self.width + x % self.width

    def direction(self, value: str) -> int:
        found = DIR.find(value)
        return max(0, found)

    def destination(self, position: int, direction: int,
                    check_body: bool = True) -> int:
        edge = self.tiles[position].edges[direction]
        if edge != ".":
            return -1  # Python v1 intentionally treats portals conservatively.
        target = self.pos(position % self.width + DX[direction],
                          position // self.width + DY[direction])
        if not self.tiles[target].visible:
            return -2
        if check_body and self.tiles[target].occupied:
            return -1
        return target

    def set_edge(self, position: int, direction: int, symbol: str) -> None:
        self.tiles[position].edges[direction] = symbol
        self.known_edges[position][direction] = symbol
        self.known_edge[position] = True

    def read_turn(self, stream: TextIO) -> bool:
        round_value = _field(stream, "ROUND")
        facing = _field(stream, "DIR")
        length = _field(stream, "LENGTH")
        units = _field(stream, "UNIT_COUNT")
        count = _field(stream, "NUM_MSGS")
        if None in (round_value, facing, length, units, count):
            return False
        self.round, self.facing = int(round_value), self.direction(facing)
        self.length, self.units = int(length), int(units)
        self.messages = []
        self.asked_to_move = False
        for _ in range(int(count)):
            values = _parts(stream)
            if not values:
                return False
            message = int(values[0])
            self.messages.append(message)
            self.asked_to_move |= message == MOVE_ASIDE

        self.tiles = [Tile(edges=list(self.known_edges[p]) if self.known_edge[p]
                           else ["."] * 4) for p in range(self.width * self.height)]
        self.friendly_sizes.clear()
        observed_enemies: dict[int, int] = {}
        window: list[int] = []
        first = _parts(stream)
        if first and first[0] == "ECHOES":
            first = _parts(stream)
        for index in range(49):
            values = first if index == 0 else _parts(stream)
            if len(values) < 4:
                return False
            x, y, pearl, countdown = map(int, values[:4])
            position = self.pos(x, y)
            window.append(position)
            tile = self.tiles[position]
            tile.visible = True
            tile.pearl = bool(pearl)
            tile.countdown = countdown
            self.known_pearls[position] = (bool(pearl), countdown, self.round)
        self.head = window[24]
        self.visits[self.head] = min(255, self.visits[self.head] + 1)

        bodies = _field(stream, "DRAGON_BODIES")
        if bodies is None:
            return False
        for _ in range(int(bodies)):
            values = _parts(stream)
            if len(values) < 6:
                return False
            team, dragon, x, y, body_facing, is_head = values[:6]
            dragon_id, position = int(dragon), self.pos(int(x), int(y))
            tile = self.tiles[position]
            tile.occupied = True
            tile.pearl = False
            tile.dragon_id = dragon_id
            tile.body_direction = self.direction(body_facing)
            tile.own_body = team == self.team and dragon_id == self.dragon_id
            if team != self.team:
                observed_enemies[dragon_id] = observed_enemies.get(dragon_id, 0) + 1
                memory = self.enemies.setdefault(dragon_id, EnemyMemory())
                memory.position, memory.last_seen = position, self.round
            elif dragon_id != self.dragon_id:
                self.friendly_sizes[dragon_id] = self.friendly_sizes.get(dragon_id, 0) + 1
            if int(is_head):
                tile.facing = self.direction(body_facing)
                tile.friendly_head = team == self.team
                tile.enemy_head = team != self.team
                if tile.enemy_head:
                    self.enemies[dragon_id].facing = tile.facing
        for dragon_id, memory in self.enemies.items():
            seen_size = observed_enemies.get(dragon_id)
            memory.visible_size = (max(seen_size, memory.visible_size - 1)
                                   if seen_size is not None else max(0, memory.visible_size - 1))

        for row in range(8):
            values = _parts(stream)
            if len(values) < 7:
                return False
            for col, symbol in enumerate(values[:7]):
                if row < 7:
                    self.set_edge(window[row * 7 + col], 0, symbol)
                if row > 0:
                    self.set_edge(window[(row - 1) * 7 + col], 2, symbol)
        for row in range(7):
            values = _parts(stream)
            if len(values) < 8:
                return False
            for col, symbol in enumerate(values[:8]):
                if col < 7:
                    self.set_edge(window[row * 7 + col], 3, symbol)
                if col > 0:
                    self.set_edge(window[row * 7 + col - 1], 1, symbol)
        self._update_features(len(observed_enemies))
        return True

    def _update_features(self, enemy_count: int) -> None:
        friendly_count = len(self.friendly_sizes) + 1
        features = self.features
        if features.round == 0:
            features.friendly_density_ewma = float(friendly_count)
            features.enemy_density_ewma = float(enemy_count)
        else:
            features.friendly_density_ewma += EWMA_ALPHA * (
                friendly_count - features.friendly_density_ewma)
            features.enemy_density_ewma += EWMA_ALPHA * (
                enemy_count - features.enemy_density_ewma)
        features.round = self.round
        features.own_length = self.length
        features.team_units = self.units
        features.visible_friendly_dragons = friendly_count
        features.visible_enemy_dragons = enemy_count

    def enemy_reach(self) -> set[int]:
        result: set[int] = set()
        for position, tile in enumerate(self.tiles):
            if not tile.enemy_head:
                continue
            result.add(position)
            for direction in range(4):
                target = self.destination(position, direction, False)
                if target >= 0:
                    result.add(target)
        return result

    def route(self, predicate, blocked: set[int] | None = None,
              cap: int | None = None) -> tuple[int, int] | None:
        blocked = blocked or set()
        distance = [-1] * len(self.tiles)
        first = [-1] * len(self.tiles)
        queue = deque([self.head])
        distance[self.head] = 0
        visited = 0
        while queue and (cap is None or visited < cap):
            position = queue.popleft()
            visited += 1
            if position != self.head and predicate(position, distance[position]):
                return first[position], distance[position]
            for direction in range(4):
                target = self.destination(position, direction)
                if target < 0 or target in blocked or distance[target] >= 0:
                    continue
                distance[target] = distance[position] + 1
                first[target] = direction if position == self.head else first[position]
                queue.append(target)
        return None

