"""64-bit packing tests for the suicide command message."""

from pathlib import Path
import sys
import unittest

BOT = Path(__file__).resolve().parents[1] / "bots/formatted-hunter-v22-python"
sys.path.insert(0, str(BOT))

from src.communications.sucide_command import SuicideCommand, SuicidePayload
from src.communications.signals import Message as Signal


class FakeController:
    def __init__(self, dragon_id=513, size=37, incoming=()):
        self.dragon_id = dragon_id
        self.size = size
        self.incoming = list(incoming)
        self.sent = []

    def get_id(self):
        return self.dragon_id

    def get_length(self):
        return self.size

    def send_sonar(self, packet):
        self.sent.append(packet)
        return True

    def get_sonar_messages(self):
        return self.incoming


class SuicideCommandTest(unittest.TestCase):
    def test_round_trip_preserves_id_and_size(self):
        packet = SuicideCommand.encode(1000, 2000, 7)
        self.assertLess(packet, 1 << 64)
        self.assertEqual(SuicideCommand.decode(packet), SuicidePayload(1000, 2000, 7))
        self.assertEqual(packet >> 60, 7)
        self.assertEqual(packet & ((1 << 39) - 1), 0)

    def test_send_reads_controller_identity(self):
        controller = FakeController()
        self.assertTrue(SuicideCommand().send(controller, 10))
        self.assertEqual(SuicideCommand.decode(controller.sent[0]),
                         SuicidePayload(513, 37, 10))

    def test_receive_filters_other_packets(self):
        packet = SuicideCommand.encode(9, 12, Signal.SUICIDE.value)
        controller = FakeController(incoming=[0, packet, 123])
        self.assertEqual(SuicideCommand().receive(controller),
                         [SuicidePayload(9, 12, Signal.SUICIDE.value)])

    def test_rejects_values_that_do_not_fit(self):
        for dragon_id, size in ((-1, 2), (1001, 2), (1, -1), (1, 2001)):
            with self.subTest(dragon_id=dragon_id, size=size):
                with self.assertRaises(ValueError):
                    SuicideCommand.encode(dragon_id, size, 10)

    def test_rejects_signal_type_larger_than_four_bits(self):
        for signal_type in (-1, 16):
            with self.assertRaises(ValueError):
                SuicideCommand.encode(1, 2, signal_type)


if __name__ == "__main__":
    unittest.main()
