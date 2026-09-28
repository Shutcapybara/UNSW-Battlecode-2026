from __future__ import annotations

from dataclasses import dataclass

from helper import Controller, Game

from ..actions import Action
from .message import Message
from .signals import Message as Signal
# Packet layout, from most to least significant bit:
#   60..63  reserved message type (4 bits)
#   50..59  dragon id            (10 bits, validated to 0..1000)
#   39..49  dragon length        (11 bits, validated to 0..2000)
#   0..38   unused ( these will need to be for validation/checksum)

TYPE_BITS = 4
ID_BITS = 10
SIZE_BITS = 11

MAX_DRAGON_ID = 1000
MAX_DRAGON_SIZE = 2000
TYPE_MASK = (1 << TYPE_BITS) - 1
ID_MASK = (1 << ID_BITS) - 1
SIZE_MASK = (1 << SIZE_BITS) - 1
TYPE_SHIFT = 60
ID_SHIFT = 50
SIZE_SHIFT = 39
MAX_PACKET = (1 << 64) - 1


@dataclass(frozen=True, slots=True)
class SuicidePayload:
    dragon_id: int
    size: int
    signal_type: int


@dataclass(frozen=True, slots=True)
class SuicideAction(Action):
    request: SuicidePayload

    def perform(self, ct: Controller, game: Game) -> bool:
        """Sacrifice us late when the requesting dragon has priority."""
        if game.get_round_num() < 450:
            return False
        sender_is_superior = (self.request.size > ct.get_length()
                              or self.request.dragon_id < ct.get_id())
        if not sender_is_superior:
            return False
        ct.make_move(ct.get_dir().get_opposite())
        return True


class SuicideCommand(Message):
    """Broadcast this dragon's id and size before a deliberate suicide action.
    """

    @staticmethod
    def encode(dragon_id: int, size: int, signal_type: int) -> int:
        if not 0 <= dragon_id <= MAX_DRAGON_ID:
            raise ValueError(f"dragon id must be between 0 and {MAX_DRAGON_ID}")
        if not 0 <= size <= MAX_DRAGON_SIZE:
            raise ValueError(f"dragon size must be between 0 and {MAX_DRAGON_SIZE}")
        if not 0 <= signal_type <= TYPE_MASK:
            raise ValueError("signal type must be a four-bit number between 0 and 15")
        packet = ((signal_type & TYPE_MASK) << TYPE_SHIFT
                  | (dragon_id & ID_MASK) << ID_SHIFT
                  | (size & SIZE_MASK) << SIZE_SHIFT)
        if packet > MAX_PACKET:
            raise ValueError("suicide command exceeds the 64-bit sonar limit")
        return packet

    @staticmethod
    def decode(packet: int, expected_type: int | None = None) -> SuicidePayload | None:
        if not 0 <= packet <= MAX_PACKET:
            return None
        signal = (packet >> TYPE_SHIFT) & TYPE_MASK
        if expected_type is not None and signal != expected_type:
            return None
        dragon_id = (packet >> ID_SHIFT) & ID_MASK
        size = (packet >> SIZE_SHIFT) & SIZE_MASK
        return SuicidePayload(dragon_id, size, signal)

    def send(self, ct: Controller, signal_type: int) -> bool:
        packet = self.encode(ct.get_id(), ct.get_length(), signal_type)
        return ct.send_sonar(packet)

    def receive(self, ct: Controller,
                signal_type: int = Signal.SUICIDE.value) -> list[SuicidePayload]:
        decoded = (self.decode(packet, signal_type)
                   for packet in ct.get_sonar_messages())
        return [payload for payload in decoded if payload is not None]

    def action(self, payload: SuicidePayload) -> Action:
        return SuicideAction(payload)
