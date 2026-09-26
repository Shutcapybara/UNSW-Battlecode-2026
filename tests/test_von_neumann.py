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
