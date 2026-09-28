"""Tests for message-type dispatch from the leading four bits."""

from pathlib import Path
import sys
import unittest

BOT = Path(__file__).resolve().parents[1] / "bots/formatted-hunter-v22-python"
sys.path.insert(0, str(BOT))

from src.communications.read_message import act_on_messages, read_message, read_messages
from src.communications.signals import Message as Signal
from src.actions import Action
from src.communications.suicide_command import SuicideAction, SuicideCommand, SuicidePayload


class FakeController:
    def __init__(self, packets, dragon_id=20, size=10):
        self.packets = packets
        self.dragon_id = dragon_id
        self.size = size
        self.moves = []

    def get_sonar_messages(self):
        return self.packets

    def get_id(self):
        return self.dragon_id

    def get_length(self):
        return self.size

    def get_dir(self):
        return FakeDirection()

    def make_move(self, direction):
        self.moves.append(direction)


class FakeDirection:
    def get_opposite(self):
        return "backwards"


class FakeGame:
    def __init__(self, round_number):
        self.round_number = round_number

    def get_round_num(self):
        return self.round_number


class ReadMessageTest(unittest.TestCase):
    def test_suicide_action_implements_action_interface(self):
        action = SuicideAction(SuicidePayload(1, 2, Signal.SUICIDE.value))
        self.assertIsInstance(action, Action)

    def test_dispatches_suicide_packet_to_its_class(self):
        packet = SuicideCommand.encode(321, 1999, Signal.SUICIDE.value)
        decoded = read_message(packet)
        self.assertEqual(decoded.signal, Signal.SUICIDE)
        self.assertEqual(decoded.payload,
                         SuicidePayload(321, 1999, Signal.SUICIDE.value))

    def test_unknown_four_bit_type_is_ignored(self):
        self.assertIsNone(read_message(15 << 60))

    def test_reads_all_recognised_controller_messages(self):
        packet = SuicideCommand.encode(7, 42, Signal.SUICIDE.value)
        decoded = read_messages(FakeController([15 << 60, packet, 0]))
        self.assertEqual(len(decoded), 1)
        self.assertEqual(decoded[0].payload.dragon_id, 7)

    def test_suicide_action_requires_round_450(self):
        packet = SuicideCommand.encode(7, 42, Signal.SUICIDE.value)
        controller = FakeController([packet])
        self.assertFalse(act_on_messages(controller, FakeGame(449)))
        self.assertEqual(controller.moves, [])
        self.assertTrue(act_on_messages(controller, FakeGame(450)))
        self.assertEqual(controller.moves, ["backwards"])

    def test_suicide_action_accepts_larger_or_lower_id_sender(self):
        cases = [
            (SuicideCommand.encode(30, 11, Signal.SUICIDE.value), True),
            (SuicideCommand.encode(19, 5, Signal.SUICIDE.value), True),
            (SuicideCommand.encode(30, 5, Signal.SUICIDE.value), False),
        ]
        for packet, expected in cases:
            with self.subTest(packet=packet):
                controller = FakeController([packet], dragon_id=20, size=10)
                self.assertEqual(act_on_messages(controller, FakeGame(450)), expected)


if __name__ == "__main__":
    unittest.main()
