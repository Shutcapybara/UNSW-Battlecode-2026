from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from ..core.model import Decision
from ..state.world import World

Condition = Callable[[World], bool]


class DecisionRule(ABC):
    def __init__(self) -> None:
        self.requirements: list[Condition] = []
        self.triggers: list[Condition] = []

    def require(self, condition: Condition) -> None:
        self.requirements.append(condition)

    def fire_on(self, condition: Condition) -> None:
        self.triggers.append(condition)

    def evaluate(self, world: World) -> Decision | None:
        if not all(condition(world) for condition in self.requirements):
            return None
        if self.triggers and not any(condition(world) for condition in self.triggers):
            return None
        return self.choose(world)

    @abstractmethod
    def choose(self, world: World) -> Decision | None:
        raise NotImplementedError

