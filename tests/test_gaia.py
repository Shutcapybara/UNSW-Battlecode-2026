"""Focused Gaia invariants.

The broader tournament remains the strategy gate; these tests keep the new
coordination and safety contracts cheap to run while iterating.
"""
import subprocess
import sys
import unittest
from unittest.mock import patch

BOT = sys.argv.pop(1)
sys.argv = ["test_bot.py", "unused"]
sys.path.insert(0, "tests")
from test_bot import turn  # noqa: E402

GAIA_DIR = BOT.rsplit("/", 1)[0]
sys.path.insert(0, GAIA_DIR)
import comms  # noqa: E402
import gaia  # noqa: E402
import world  # noqa: E402


def run(block, bot=BOT, dragon_id=0):
    result = subprocess.run(
        [sys.executable, bot],
        input=f"ID {dragon_id}\nTEAM A\nMAP 11 11\nUNIT_LIMIT 64\n" + block,
        capture_output=True, text=True, check=True, timeout=5,
    )
    return result.stdout.splitlines()


class GaiaSafety(unittest.TestCase):
    def test_guidance_sonar_round_trips(self):
        world.TEAM = "A"
        world.W = world.H = 11
        world.NC = 121
        world.RND = 3
        lines = run(turn(length=2).replace("ROUND 1", "ROUND 3"))
        packets = [int(line.split()[2]) for line in lines if line.startswith("SONAR ")]
        decoded = []
        for packet in packets:
            unpacked = comms.unpack(packet)
            if unpacked and unpacked[0] == comms.T_GUIDANCE:
                decoded.append(comms.guidance_decode(unpacked[1]))
        self.assertTrue(decoded)
        self.assertEqual(decoded[0][0], 0)
        self.assertEqual(decoded[0][4], 3)

    def test_blind_portal_is_gated_for_non_scouts_in_opening(self):
        lines = run(turn(length=2, portals=[("v", 3, 4, "1")]), dragon_id=1)
        self.assertFalse(lines[0] == "MOVE E")

    def test_dead_pearl_requires_post_collection_exit(self):
        body = [1, 2, 3]
        with patch.object(gaia.tx, "exits", return_value=0), \
             patch.object(gaia.tx, "flood", return_value=0):
            self.assertFalse(gaia.pearl_escape_safe(body))
        with patch.object(gaia.tx, "exits", return_value=1), \
             patch.object(gaia.tx, "flood", return_value=10):
            self.assertTrue(gaia.pearl_escape_safe(body))

    def test_threatened_pearl_exit_is_not_safe(self):
        if gaia.pearl_escape_safe.__code__.co_argcount < 2:
            self.skipTest("candidate predates threat-aware pearl exits")
        body = [1, 2, 3]
        world.occ = {}
        with patch.object(gaia.w, "dest", return_value=[4, -1, -1, -1]), \
             patch.object(gaia.tx, "flood", return_value=10):
            self.assertFalse(gaia.pearl_escape_safe(body, {4: [(1, 9, 3)]}))

    def test_threat_pearl_gate_is_medium_map_only(self):
        if not hasattr(gaia, "P") or "threat_pearl_min_area" not in gaia.P:
            self.skipTest("candidate predates the medium-map threat gate")
        body = [1, 2, 3]
        old_w, old_h, old_nc = world.W, world.H, world.NC
        old_body, old_len, old_head = world.body, world.LEN, world.HEAD
        world.occ = {}
        world.body = list(body)
        world.LEN = len(body)
        world.HEAD = body[-1]
        try:
            with patch.object(gaia.w, "dest", return_value=[4, -1, -1, -1]), \
                 patch.object(gaia.tx, "flood", return_value=10):
                world.W = world.H = 32
                world.NC = world.W * world.H
                self.assertFalse(gaia.safe_move([0], body, 1,
                                                 {4: [(1, 9, 3)]}))
                world.W = world.H = 11
                world.NC = world.W * world.H
                self.assertTrue(gaia.safe_move([0], body, 1,
                                                {4: [(1, 9, 3)]}))
        finally:
            world.W, world.H, world.NC = old_w, old_h, old_nc
            world.body, world.LEN, world.HEAD = old_body, old_len, old_head

    def test_tiny_opening_rejects_zero_exit_moves(self):
        if not hasattr(gaia, "P") or "tiny_opening_exit_area" not in gaia.P:
            self.skipTest("candidate predates the tiny opening exit guard")
        body = [1, 2, 3]
        old_w, old_h, old_nc, old_rnd = world.W, world.H, world.NC, world.RND
        try:
            world.W = world.H = 11
            world.NC = world.W * world.H
            world.RND = 50
            with patch.object(gaia.tx, "exits", return_value=0):
                self.assertFalse(gaia.safe_move([0], body, 0))
            world.W = world.H = 32
            world.NC = world.W * world.H
            with patch.object(gaia.tx, "exits", return_value=0):
                self.assertTrue(gaia.safe_move([0], body, 0))
        finally:
            world.W, world.H, world.NC, world.RND = old_w, old_h, old_nc, old_rnd

    def test_split_legal_bounds_are_checked(self):
        world.LEN = 6
        world.UNITS = 4
        world.LIMIT = 64
        self.assertTrue(gaia.split_legal(2))
        self.assertTrue(gaia.split_legal(3))
        self.assertTrue(gaia.split_legal(4))
        self.assertFalse(gaia.split_legal(5))

    def test_breeding_evidence_counts_spawn_transitions_once(self):
        if not hasattr(gaia, "SPAWN_EVENTS"):
            self.skipTest("candidate predates event-based breeding evidence")
        world.W = world.H = 11
        world.NC = 121
        world.RND = 1
        world.seen = [1] * world.NC
        gaia.init()
        with patch.object(gaia.w, "io_tiles", side_effect=(
                [(1, 1, False, 3)],
                [(1, 1, True, 0)],
                [(1, 1, True, 0)])):
            gaia._observe_resources()
            gaia._observe_resources()
            gaia._observe_resources()
        self.assertEqual(gaia.SPAWN_EVENTS[12], 1)

    def test_repeated_spawn_evidence_is_eligible_for_sonar(self):
        if not hasattr(gaia, "_best_spawn_cell"):
            self.skipTest("candidate predates spawn-rate sonar")
        old_w, old_h, old_nc, old_bed = world.W, world.H, world.NC, world.bed
        try:
            world.W = world.H = 11
            world.NC = 121
            world.bed = bytearray(world.NC)
            world.bed[12] = 2
            gaia.init()
            gaia.SPAWN_EVENTS[12] = 2
            self.assertEqual(gaia._best_spawn_cell(), 12)
        finally:
            world.W, world.H, world.NC, world.bed = old_w, old_h, old_nc, old_bed

    def test_opening_lanes_cover_four_global_id_sectors(self):
        lane = getattr(gaia, "explore_direction", None)
        if lane is None and hasattr(gaia, "FOUR_WAY_SECTORS"):
            lane = gaia.preferred_direction
        if lane is None:
            self.skipTest("candidate does not use four-way global-ID sectors")
        world.TEAM = "A"
        for dragon_id in range(4):
            world.ME = dragon_id
            self.assertEqual(lane(), dragon_id)

    def test_opening_threat_veto_is_limited_to_growth_window(self):
        if not hasattr(gaia, "opening_threatened"):
            self.skipTest("candidate predates the opening threat shield")
        world.RND = 50
        world.HEAD = 0
        world.enemy_heads = [(3, 9)]
        with patch.object(gaia.w, "tdist", return_value=3):
            self.assertTrue(gaia.opening_threatened(4, {4: [(1, 9, 3)]}))
        world.enemy_heads = [(9, 9)]
        with patch.object(gaia.w, "tdist", return_value=5):
            self.assertFalse(gaia.opening_threatened(4, {4: [(1, 9, 3)]}))
        world.RND = 100
        world.enemy_heads = [(3, 9)]
        with patch.object(gaia.w, "tdist", return_value=3):
            self.assertFalse(gaia.opening_threatened(4, {4: [(1, 9, 3)]}))

    def test_arena_lane_uses_opposing_team_local_sectors(self):
        if "arena_lane_area" not in getattr(gaia, "P", {}):
            self.skipTest("candidate predates the Arena lane experiment")
        old_w, old_h, old_team, old_me = world.W, world.H, world.TEAM, world.ME
        try:
            world.W = world.H = 11
            world.TEAM = "A"
            world.ME = 0
            self.assertEqual(gaia.preferred_direction(), 0)
            world.TEAM = "B"
            world.ME = 1
            self.assertEqual(gaia.preferred_direction(), 2)
        finally:
            world.W, world.H, world.TEAM, world.ME = old_w, old_h, old_team, old_me

    def test_medium_lane_spreads_interleaved_starters(self):
        if "medium_lane_area_min" not in getattr(gaia, "P", {}):
            self.skipTest("candidate predates medium team-local lanes")
        old_w, old_h, old_team, old_me = world.W, world.H, world.TEAM, world.ME
        try:
            world.W = world.H = 32
            world.TEAM = "A"
            world.ME = 0
            self.assertEqual(gaia.preferred_direction(), 0)
            world.ME = 2
            self.assertEqual(gaia.preferred_direction(), 1)
            world.TEAM = "B"
            world.ME = 1
            self.assertEqual(gaia.preferred_direction(), 2)
            world.ME = 3
            self.assertEqual(gaia.preferred_direction(), 3)
        finally:
            world.W, world.H, world.TEAM, world.ME = old_w, old_h, old_team, old_me

    def test_terminal_input_still_emits_a_command(self):
        lines = run(turn(length=2, walls="NESW"))
        self.assertTrue(lines[0].startswith(("MOVE ", "SPLIT ")))
        self.assertEqual(lines[-1], "ENDTURN")


if __name__ == "__main__":
    unittest.main()
