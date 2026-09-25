from abc import ABC, abstractmethod
from typing import Any

from helper import Controller

from ..actions import Action


class Message(ABC):
    @abstractmethod
    def send(self, ct: Controller, signal_type: int) -> bool:
        pass

    @abstractmethod
    def receive(self, ct: Controller) -> list[Any]:
        pass

    @abstractmethod
    def action(self, payload: Any) -> Action:
        """Build the game action associated with a decoded message."""
        pass

