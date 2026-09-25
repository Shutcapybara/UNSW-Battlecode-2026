from __future__ import annotations

from abc import ABC, abstractmethod

from helper import Controller, Game


class Action(ABC):
    """Something that may issue one game action for the current turn."""

    @abstractmethod
    def perform(self, ct: Controller, game: Game) -> bool:
        """Execute the action and report whether a game action was issued."""
        raise NotImplementedError
