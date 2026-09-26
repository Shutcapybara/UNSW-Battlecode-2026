"""Contract checks for the Von Neumann combat mechanisms (bots/von_neumann-x02-mech)
and the frozen baseline's combat defaults.  Subprocess-isolated like the Porthos
suites: standalone bot imports never leak across lineages."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
X01 = ROOT / "bots/von_neumann-x01-frozen"
X02 = ROOT / "bots/von_neumann-x02-mech"

# Minimal world in which enemy head id 5 (len 6) sits in reach of our head.
SETUP = '''
import protocol as io, world as w, roles, targets
import decision
from params import P
io.game.update(id=0, team='A', size=(11, 11), unit_limit=64)
w.init(); w.ek[:] = bytes([1])*len(w.ek)
w.RND = 10; w.HEAD = 60; w.LEN = 5; w.body = [56, 57, 58, 59, 60]
w.UNITS = 3; w.elen[5] = 6; w.elen[9] = 5
roles.ROLE[0] = "forager"
H2H = {"mode": "move", "arg": [1], "exclusive": False, "emergency": False,
       "id": 0, "kind": "attack", "target": -1,
       "preview": {"outcome": "h2h", "steps": 1, "hit": 5}}
def gf(a=0.0, e=0.0, conf=0.0, early=False, sat=0.0):
    return {"early": early, "sat": sat, "lengths": (a, e, conf), "threat": {}}
def sc(a=0.0, e=0.0, conf=0.0, early=False, sat=0.0):
    return decision.score(dict(H2H), {"need": 99}, gf(a, e, conf, early, sat), {})
'''


class VonNeumannMechanismTests(unittest.TestCase):
    def check(self, code, bot=X02):
        subprocess.run([sys.executable, "-c", SETUP + code], cwd=bot, check=True)

    def test_defaults_are_p1(self):
        self.check('''
assert P["w_margin_balance"] == 0.0 and P["w_support"] == 0.0
assert decision.POLICY_VERSION == 3
# V(enemy 6) - V(me 5) = (3+6) - (3+5) = 1.0 >= atk_margin 0.5: P1 accepts
assert sc() == 3.0, sc()
''')

    def test_cm1_direction_and_gate(self):
        self.check('''
P["w_margin_balance"] = 4.0
# enemy-heavy local waters: balance = (10-2)/(12+4) = 0.5 -> margin 0.5+2.0
# gain 1.0 < 2.5: the same trade P1 accepts is now refused
assert sc(**{"a": 2.0, "e": 10.0, "conf": 1.0}) == -950.0
# allied-heavy: balance -0.5 -> margin -1.5; an even trade (gain 0) is accepted
H2H["preview"]["hit"] = 9
assert sc(**{"a": 10.0, "e": 2.0, "conf": 1.0}) == 2.0
# no evidence -> no shift: even trade still refused at the P1 margin
assert sc(**{"a": 10.0, "e": 2.0, "conf": 0.0}) == -950.0
''')

    def test_cm1_balance_values(self):
        self.check('''
assert decision.balance_at_head(gf(0, 0, 0.0)) == 0.0
b = decision.balance_at_head(gf(2.0, 10.0, 1.0))
assert abs(b - 0.5) < 1e-9, b
''')

    def test_cm2_support_bonus_and_cap(self):
        self.check('''
P["w_support"] = 1.0
# head 60 = (5,5); allies at tdist 2, 3 and 6 (outside support_r=3)
w.ally_heads = [(58, 1), (47, 2), (6, 3)]
assert decision.support_count() == 2, decision.support_count()
# even trade (gain 0 < margin 0.5) accepted with one support unit's bonus:
# gain becomes 1.0, so the score is 2.0 + 1.0
H2H["preview"]["hit"] = 9
w.ally_heads = [(58, 1)]
assert sc() == 3.0, sc()
# cap 2: a mob of allies still adds at most 2
w.ally_heads = [(58, 1), (59, 2), (70, 3), (72, 4)]
assert decision.strike_value(9, 1, 0.5 - 2.0) is not None
P["support_cap"] = 0
assert decision.strike_value(9, 1, 0.5 - 0.0) is None
''')

    def test_x01_score_parity_off(self):
        """With switches off the x02 score equals the x01 (P1) score on the
        same fabricated combat state."""
        code = '''
import json, sys
out = [sc(), decision.strike_value(5, 1, 0.5)]
sys.stdout.write(json.dumps(out))
'''
        a = subprocess.run([sys.executable, "-c", SETUP + code], cwd=X02,
                           capture_output=True, text=True, check=True)
        b = subprocess.run([sys.executable, "-c", SETUP + code], cwd=X01,
                           capture_output=True, text=True, check=True)
        self.assertEqual(a.stdout, b.stdout)


if __name__ == "__main__":
    unittest.main()


X06 = ROOT / "bots/von_neumann-x06-info"
SETUP06 = '''
import protocol as io, world as w, roles, targets
import decision, swarm, comms, features
from params import P
io.game.update(id=0, team='A', size=(11, 11), unit_limit=64)
w.init(); w.ek[:] = bytes([1])*len(w.ek)
w.RND = 10; w.HEAD = 60; w.LEN = 5; w.body = [56, 57, 58, 59, 60]
w.UNITS = 3; w.elen[5] = 6; w.elen[9] = 5
roles.ROLE[0] = "forager"
swarm.init()
H2H = {"mode": "move", "arg": [1], "exclusive": False, "emergency": False,
       "id": 0, "kind": "attack", "target": -1,
       "preview": {"outcome": "h2h", "steps": 1, "hit": 5}}
def gf(a=0.0, e=0.0, conf=0.0, early=False, sat=0.0, phase=0.0):
    return {"early": early, "sat": sat, "phase": phase, "threat": {},
            "lengths": (a, e, conf), "lengths_short": (a, e, conf)}
def sc(a=0.0, e=0.0, conf=0.0, early=False, sat=0.0, phase=0.0):
    return decision.score(dict(H2H), {"need": 99}, gf(a, e, conf, early, sat, phase), {})
'''


class VonNeumannInfoTests(unittest.TestCase):
    def check(self, code):
        subprocess.run([sys.executable, "-c", SETUP06 + code], cwd=X06, check=True)

    def test_defaults_are_p1(self):
        self.check('''
assert P["field_dual"] == 0 and P["field_room"] == 0
assert P["w_grad"] == 0 and P["w_mb2"] == 0.0 and P["w_tf"] == 0.0
assert decision.POLICY_VERSION == 4
assert decision._threat_scale(gf()) == 1.0
assert sc() == 3.0, sc()
''')

    def test_mb2_direction_gate_and_phase(self):
        self.check('''
P["w_mb2"] = 4.0
# enemy-heavy short window: balance ~ (10-2)/(12+5) = 0.47, margin +1.9 ->
# the gain-1.0 trade P1 accepts is refused
assert sc(e=10.0, a=2.0, conf=1.0) == -950.0
# allied-heavy: even trade (gain 0) accepted
H2H["preview"]["hit"] = 9
assert sc(e=2.0, a=10.0, conf=1.0) == 2.0
# no evidence -> no shift
assert sc(e=2.0, a=10.0, conf=0.0) == -950.0
# late phase halves the shift: enemy-heavy now shifts by ~0.94, so the
# gain-1.0 trade is accepted again at margin 0.5+0.94=1.44... refused still;
# check the halving numerically instead
b0 = decision.self_balance(gf(e=10.0, a=2.0, conf=1.0, phase=0.0))
b1 = decision.self_balance(gf(e=10.0, a=2.0, conf=1.0, phase=1.0))
assert abs(b1 - b0 * 0.5 / 1.0) < 1e-9, (b0, b1)
# own length damps: a long dragon reads the same field as less alarming
w.LEN = 16
b2 = decision.self_balance(gf(e=10.0, a=2.0, conf=1.0, phase=0.0))
w.LEN = 5
assert abs(b2) < abs(b0), (b0, b2)
''')

    def test_short_window_decays_faster(self):
        self.check('''
w.RND = 20
# one report 6 rounds old near cell 60: long window keeps ~0.35 amplitude,
# short window (h=1) keeps ~0.015
swarm.REPORTS[(7, 0)] = (5.0, 5.0, 0.0, 8.0, 14, None)
swarm._activate()
_, e_long, _ = swarm.field(60)
_, e_short, _ = swarm.field_short(60)
assert 0 < e_short < e_long, (e_long, e_short)
''')

    def test_threat_scale_under_contact(self):
        self.check('''
P["w_tf"] = 0.5
# contact is the short-window enemy length at the head, normalised by
# features.global_features to [0, 1] (features.contact_norm = 6.0)
assert decision._threat_scale({"contact": 0.0}) == 1.0
assert decision._threat_scale({"contact": 1.0}) == 1.5
assert abs(decision._threat_scale({"contact": 0.5}) - 1.25) < 1e-9
assert decision._threat_scale({}) == 1.0                      # missing key safe
# the normalisation itself is built only when a consumer is on
P["w_tf"] = 0.0
gf = features.global_features()
assert "contact" not in gf                                     # switch off: absent
P["w_tf"] = 1.0
gf = features.global_features()
assert "contact" in gf and gf["contact"] == 0.0                # no evidence
''')

    def test_foreign_team_tag_rejected(self):
        """Idea #7 regression: the packet layer already rejects foreign-team
        payloads (team tag byte + checksum); random enemy messages never
        reach decode."""
        self.check('''
pkt = comms.pack(comms.T_SWARM, 12345)
assert comms.unpack(pkt) is not None
w.TEAM = "B"
assert comms.unpack(pkt) is None          # other team's tag
bad = pkt ^ (1 << 40)                     # corrupted payload bit
w.TEAM = "A"
assert comms.unpack(bad) is None          # checksum mismatch
''')

    def test_spatial_gain_open_world(self):
        self.check('''
import features, tactics as tx
P["field_room"] = 1
# an ok single step in the open 11x11 world: room caps at 12 = room_norm,
# so the spatial gain equals the ordinary gain (undamped in open water)
w.elen.pop(5, None)
cand = {"mode": "move", "arg": [1], "exclusive": False, "emergency": False,
        "id": 0, "kind": "gather", "target": -1}
gf = features.global_features()
tf = features.target_features({"target": -1, "mask": {}, "dist": {},
                               "own_idx": {c: i for i, c in enumerate(w.body)}})
features.preview(cand, gf, tf)
pv = cand["preview"]
assert pv["outcome"] == "ok" and "spatial_gain" in pv and "room" in pv
assert pv["room"] == P["room_cap"]
assert abs(pv["spatial_gain"] - pv["swarm_gain"]) < 1e-12
''')
