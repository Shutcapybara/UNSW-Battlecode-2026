"""Engine-faithful scenarios and contract checks for the Porthos intention
execution layer (bots/porthos-x02-intentions).  Subprocess-isolated like the
Monte Christo density checks: standalone bot imports never leak across
lineages."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOT = ROOT / "bots/porthos-x02-intentions"
SETUP = '''
import protocol as io, world as w, tactics as tx, roles, comms
import targets, intentions, features, decision, executors
from params import P
io.game.update(id=0, team='A', size=(11,11), unit_limit=64)
w.init(); w.ek[:] = bytes([1])*len(w.ek)
w.RND=10; w.HEAD=60; w.LEN=3; w.body=[58,59,60]
GF = features.global_features()
def pipe():
    cands, ctx = intentions.propose()
    gf = features.global_features()
    tf = features.target_features(ctx)
    for c in cands: features.preview(c, gf, tf)
    sel, ranked = decision.choose(cands, tf, gf["threat"])
    return sel, ranked, executors.execute(sel)
'''


class EngineScenarioTests(unittest.TestCase):
    def check(self, code, bot=BOT):
        subprocess.run([sys.executable, '-c', SETUP + code], cwd=bot, check=True)

    def test_wrapping_move(self):
        self.check('''
w.body=[9,10]; w.HEAD=10; w.LEN=2
st, nb, eaten, hit = tx.sim([1], w.body)
assert (st, nb) == ('ok', [10, 0]), (st, nb)
st, nb, eaten, hit = tx.sim([0], w.body)
assert (st, nb) == ('ok', [10, 120]), (st, nb)
''')

    def test_portal_paired_and_unpaired(self):
        self.check('''
k1 = w.ekey(60, 1); k2 = w.ekey(80, 3)
w.learn_pair(k1, k2, 5)
assert w.dest(60)[1] == 80
assert tx.sim([1], w.body)[0] == 'ok'
k3 = w.ekey(60, 0)
w.ek[k3] = 3; w.epid[k3] = 99; w.pends[99] = [k3]
w.DC[60] = None
assert tx.sim([0], w.body)[0] == 'dive'
k4 = w.ekey(71, 0)
w.ek[k4] = 3; w.epid[k4] = 98; w.pends[98] = [k4]
w.DC[71] = None
assert tx.sim([2, 0], w.body)[0] == 'dead'       # unpaired portal mid-sprint
''')

    def test_tail_occupancy_and_sprint_cost(self):
        self.check('''
assert tx.sim([3], w.body)[0] == 'dead'          # own body segment
w.body=[49, 50, 61, 60]; w.LEN=4
assert tx.sim([0], w.body)[0] == 'dead'          # tail not yet vacated
w.body=[58, 59, 60]; w.LEN=3
assert tx.sim([1, 1], w.body)[:3] == ('ok', [61, 62], 0)
assert tx.sim([1, 1, 1], w.body)[0] == 'dead'    # length ran out
w.pearls[61] = w.RND
assert tx.sim([1, 1, 1], w.body)[:3] == ('ok', [62, 63], 1)
''')

    def test_head_trades_and_strike_gate(self):
        self.check('''
w.occ[61] = (7, False, True); w.elen[7] = 8; w.UNITS = 5
assert tx.sim([1], w.body)[0::3] == ('h2h', 7)
assert decision.strike_value(7, 1) == 2.0 + 5.0  # 8+3 vs 3+3, gain 5
w.elen[7] = 3
assert decision.strike_value(7, 1) is None       # even trade below margin
w.occ[61] = (7, True, True)
assert decision.strike_value(7, 1) is None       # never a friend
''')

    def test_legal_split_geometry(self):
        self.check('''
w.LEN=4; w.body=[57,58,59,60]; w.UNITS=2
assert intentions.reproduce_available() == 2
w.UNITS = w.LIMIT
assert intentions.reproduce_available() is None
w.UNITS = 2; w.occ[46] = (9, False, False); w.occ[56] = (9, False, False); w.occ[68] = (9, False, False)
assert intentions.reproduce_available() is None  # child has no exit
''')

    def test_child_uses_born_search_cap(self):
        self.check('''
own = {c: i for i, c in enumerate(w.body)}
w.BORN = w.RND
targets.choose_target(own)                       # cold caches, small cap
assert w.RND - w.BORN < 2
w.BORN = w.RND - 5
targets.choose_target(own)
assert P["born_cap"] < P["big_cap"]
''')

    def test_intentional_feeding_is_explicit(self):
        self.check('''
roles.ROLE[0] = 'feeder'
w.crown = [7, 61, 10, w.RND]; w.ally_heads = [(61, 7)]
d = intentions.donation_move()
assert d == 3, d                                  # back into our own body: dies
cand = {"id": 0, "kind": "feed_ally", "target": 61, "mode": "move",
        "arg": [d], "exclusive": True, "emergency": False, "score": 0.0}
features.preview(cand, GF, {"prog": [0]*4, "crown_flank": set(), "need": 5})
rec = executors.execute(cand)
assert rec["predicted"] == 'dead' and rec["trade"] == 'donation'
assert rec["status"] == 'completed'               # the objective, not a failure
''')

    def test_donation_is_exclusive(self):
        self.check('''
roles.ROLE[0] = 'feeder'
w.crown = [7, 61, 10, w.RND]; w.ally_heads = [(61, 7)]
cands, ctx = intentions.propose()
assert len(cands) == 1 and cands[0]["exclusive"] and cands[0]["kind"] == 'feed_ally'
''')


class ContractTests(unittest.TestCase):
    def check(self, code, bot=BOT):
        subprocess.run([sys.executable, '-c', SETUP + code], cwd=bot, check=True)

    def test_preview_commits_nothing(self):
        self.check('''
cands, ctx = intentions.propose()
mem0 = dict(targets.MEM); trail0 = list(w.trail); body0 = list(w.body)
gf = features.global_features(); tf = features.target_features(ctx)
for c in cands: features.preview(c, gf, tf)
assert dict(targets.MEM) == mem0                   # previews never re-commit
assert list(w.trail) == trail0 and list(w.body) == body0
''')

    def test_no_surviving_move_is_recorded_but_legal(self):
        self.check('''
w.LEN=2; w.body=[59,60]; w.HEAD=60
for c in (49, 61, 71): w.occ[c] = (9, False, False)
sel, ranked, rec = pipe()
assert rec["status"] == 'fallback' and rec["reason"] == 'no-surviving-move'
assert rec["command"][0] == 'move'                 # still a valid engine command
''')

    def test_emergency_split_gated_by_despair(self):
        self.check('''
w.RND=400                                        # production window closed
w.LEN=5; w.body=[56,57,58,59,60]; w.HEAD=60
for c in (49, 61, 71): w.occ[c] = (9, False, False)
sel, ranked, rec = pipe()
assert sel["kind"] == 'retreat' and rec["command"] == ('split', 3), (sel, rec)
del w.occ[61]                                      # one exit: no despair
sel, ranked, rec = pipe()
assert sel["mode"] == 'move' and all(not c["emergency"] for c in ranked)
''')

    def test_executor_menu_and_record_interface(self):
        self.check('''
assert set(executors.EXECUTORS) == set(intentions.KINDS)
w.LEN=4; w.body=[57,58,59,60]; w.UNITS=2
sel, ranked, rec = pipe()
for k in ("command","predicted","status","reason","trade","path_cells","report","diag"):
    assert k in rec, k
assert rec["command"] in (("split", 2), rec["command"])
''')

    def test_crown_handoff_on_majority_split(self):
        self.check('''
import main as m
io.observation.update(tiles=[], messages=[])
w.RND=300; w.LEN=10; w.body=list(range(50,60)); w.HEAD=59; w.FACE=0
roles.ROLE[0] = 'crown'; w.crown = [w.ME & 4095, 59, 10, w.RND]
m.work.clear(); m.work["exec"] = {"command": ("split", 6)}
m.construct_messages()
msg = m.work["messages"]["S"]                      # back ray of FACE=N
assert comms.handoff_decode(comms.unpack(msg)[1]) == (6, 300)
m.work["exec"] = {"command": ("split", 4)}         # child not majority: no handoff
m.construct_messages()
assert comms.unpack(m.work["messages"]["S"])[0] != comms.T_HANDOFF
''')

    def test_traces_stay_disabled_in_deployment(self):
        self.check('''
assert P["intent_trace"] == 0 and P["training_trace"] == 0
''')

    def test_protocol_is_unmodified_bahamut_adapter(self):
        self.assertEqual((BOT / 'protocol.py').read_bytes(),
                         (ROOT / 'examples/bahamut-scaffold/protocol.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
