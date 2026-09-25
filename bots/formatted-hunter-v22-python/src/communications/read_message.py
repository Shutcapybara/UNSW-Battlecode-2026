from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from helper import Controller, Game

from .signals import Message as Signal
from .sucide_command import SuicideCommand


TYPE_SHIFT = 60
TYPE_MASK = 0xF

# This is the single association table between wire types and implementations.
# Add one entry here whenever a new member is added to signals.Message.
MESSAGE_CLASSES = {
    Signal.SUICIDE: SuicideCommand,
}


@dataclass(frozen=True, slots=True)
class ReceivedMessage:
    signal: Signal
    payload: Any


def _validate_registry() -> None:
    missing = set(Signal) - set(MESSAGE_CLASSES)
    extra = set(MESSAGE_CLASSES) - set(Signal)
    if missing or extra:
        raise RuntimeError(
            f"message registry does not match signals.Message; "
            f"missing={sorted(item.name for item in missing)}, "
            f"extra={sorted(item.name for item in extra)}"
        )


_validate_registry()


def read_message(packet: int) -> ReceivedMessage | None:
    """Decode one 64-bit packet using its leading four-bit message type."""
    if not 0 <= packet < 1 << 64:
        return None
    type_number = (packet >> TYPE_SHIFT) & TYPE_MASK
    try:
        signal = Signal(type_number)
    except ValueError:
        return None

    message_class = MESSAGE_CLASSES.get(signal)
    if message_class is None:
        return None
    payload = message_class.decode(packet, signal.value)
    if payload is None:
        return None
    return ReceivedMessage(signal, payload)


def read_messages(ct: Controller) -> list[ReceivedMessage]:
    """Decode every recognised sonar packet currently held by a controller."""
    decoded = (read_message(packet) for packet in ct.get_sonar_messages())
    return [message for message in decoded if message is not None]


def act_on_messages(ct: Controller, game: Game) -> bool:
    """Dispatch received packets and stop after the first issued game action."""
    for received in read_messages(ct):
        message_class = MESSAGE_CLASSES[received.signal]
        action = message_class().action(received.payload)
        if action.perform(ct, game):
            return True
    return False
