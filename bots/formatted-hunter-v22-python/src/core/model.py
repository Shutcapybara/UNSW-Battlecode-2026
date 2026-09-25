from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Execution(Enum):
    PORTAL_TRIP = auto()
    SURVIVE = auto()
    GROW = auto()
    ATTACK = auto()
    YIELD = auto()
    SPLIT = auto()
    ADVANCE = auto()
    FORAGE = auto()
    EXPLORE = auto()
    FALLBACK = auto()


@dataclass(slots=True)
class Decision:
    execution: Execution
    command: str


@dataclass(slots=True)
class Tile:
    visible: bool = False
    pearl: bool = False
    occupied: bool = False
    own_body: bool = False
    countdown: int = -1
    friendly_head: bool = False
    enemy_head: bool = False
    dragon_id: int = -1
    facing: int = -1
    body_direction: int = -1
    edges: list[str] = field(default_factory=lambda: ["."] * 4)


@dataclass(slots=True)
class EnemyMemory:
    position: int = -1
    visible_size: int = 0
    facing: int = -1
    last_seen: int = -1


@dataclass(slots=True)
class MacroFeatures:
    round: int = 0
    own_length: int = 0
    team_units: int = 0
    visible_friendly_dragons: int = 0
    visible_enemy_dragons: int = 0
    friendly_density_ewma: float = 0.0
    enemy_density_ewma: float = 0.0


@dataclass(slots=True)
class LocalSafety:
    reachable_tiles: int = 0
    immediate_exits: int = 0
    enemy_reachable_tiles: int = 0
    dead_end: bool = True

