"""Scenario and contract checks for the Porthos x03 generation
(bots/porthos-x03-swarm, porthos-x04-policy, porthos-x05-recon):
directional length-density communication, game-relative features, the P1
policy consumers, and the portal-recon executor.  Subprocess-isolated like
the other lineage checks: bot modules never leak across versions."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
X03 = ROOT / "bots/porthos-x03-swarm"
X04 = ROOT / "bots/porthos-x04-policy"
X05 = ROOT / "bots/porthos-x05-recon"

SETUP = '''
import protocol as io, world as w, tactics as tx, roles, comms
import targets, intentions, features, decision, executors, density, swarm, radio
from params import P
io.game.update(id=0, team='A', size=(11,11), unit_limit=64)
io.observation.update(tiles=[], messages=[])
w.init(); w.ek[:] = bytes([1])*len(w.ek)
density.init(); swarm.init()
w.RND=10; w.HEAD=60; w.LEN=3; w.body=[58,59,60]
swarm.observe([(58,1),(59,1)]); density.observe()
GF = features.global_features()
'''


def run(code, bot):
    subprocess.run([sys.executable, '-c', SETUP + code], cwd=bot, check=True)


class SwarmPacketTests(unittest.TestCase):
    def test_swarm_packet_round_trip_and_bounds(self):
        run('''
p = comms.swarm_packet(7, 5, 5, 2, 3.4, 99.0, 10)
d = comms.swarm_decode(comms.unpack(p)[1])
assert d == (7, 5, 5, 2, 3.0, 15.0, 10), d          # enemy length saturates
assert comms.swarm_packet(7, 5, 5, 0, 0, 0, 500) is None   # rounds >= 500: disabled
p_future = comms.swarm_packet(7, 5, 5, 0, 1, 1, 11)  # future round: decode rejects
assert comms.swarm_decode(comms.unpack(p_future)[1]) is None
assert comms.swarm_packet(9000, 5, 5, 0, 1, 1, 10) is None   # sender id too big
p_foreign = comms.swarm_packet(7, 5, 5, 0, 1, 1, 10) ^ 0xD3  # wrong tag
assert comms.unpack(p_foreign) is None
''', X03)

    def test_density_packet_round_trip(self):
        run('''
p = comms.density_packet(9, 4.6, 5.4, 3.0, 47.0, 10)
d = comms.density_decode(comms.unpack(p)[1])
assert d == (9, 5, 5, 3.0, 31.0, 10), d             # counts saturate at 31
''', X03)

    def test_quadrant_partition_total(self):
        run('''
seen = {}
for dx in range(-3, 4):
    for dy in range(-3, 4):
        q = swarm.quadrant(dx, dy)
        assert (dx, dy) not in seen                  # exactly one quadrant each
        seen[(dx, dy)] = q
assert sorted(set(seen.values())) == [0, 1, 2, 3]
assert swarm.quadrant(1, 0) == 1 and swarm.quadrant(-1, 0) == 3
assert swarm.quadrant(0, 1) == 0 and swarm.quadrant(0, -1) == 2
''', X03)


class SwarmStateTests(unittest.TestCase):
    def test_observe_counts_visible_segments(self):
        run('''
w.RND = 11
w.occ[63] = (9, False, True)     # q1 enemy head
w.occ[61] = (9, False, False)    # q1 enemy body
w.occ[47] = (8, True, True)      # q2 ally head
swarm.observe([(58, 1), (59, 1)])
qa, qe = swarm.CUR
assert qe[1] == 2.0 and qa[2] == 1.0 and qa[3] == 3.0, (qa, qe)  # own: 2 body + head in q3
''', X03)

    def test_hear_dedup_and_ttl(self):
        run('''
p1 = comms.swarm_packet(42, 8, 8, 0, 1, 5, 10)
radio.hear([p1]); radio.hear([p1])
assert len(swarm.REPORTS) == 1
p_old = comms.swarm_packet(43, 8, 8, 0, 1, 5, 2)     # age 8 > TTL? TTL=16 -> accepted
radio.hear([p_old])
assert len(swarm.REPORTS) == 2
stale = comms.swarm_packet(44, 8, 8, 0, 1, 5, w.RND)  # same-round older-than-self check
w.RND = 40
radio.hear([stale])                                   # age 30 > TTL: rejected
assert len(swarm.REPORTS) == 2, dict(swarm.REPORTS)
''', X03)

    def test_field_confidence_and_directional_gain(self):
        run('''
swarm.LOCAL = None                                   # no local evidence either
del swarm.ACTIVE[:]; swarm.CACHE.clear()
al, el, conf = swarm.field(20)
assert conf == 0.0 and al == 0.0 and el == 0.0       # no evidence near cell 20
pkt = comms.swarm_packet(42, 5, 5, 1, 0.0, 12.0, w.RND)  # enemy mass, quadrant 1
radio.hear([pkt])
swarm._activate()                                    # observe() does this per turn
ge = swarm.gain(62)   # east of head
gw = swarm.gain(57)   # west of head
assert ge > gw, (ge, gw)                              # gain rises toward the enemy mass
''', X03)

    def test_packet_now_contact_vs_rotation(self):
        run('''
q0 = comms.swarm_decode(comms.unpack(swarm.packet_now())[1])[3]
assert q0 == (w.RND + w.ME) % 4                        # no contact: rotation
w.RND = 11
w.occ[63] = (9, False, True); w.elen[9] = 1
w.occ[61] = (9, False, False)
swarm.observe([(58, 1), (59, 1)])
d = comms.swarm_decode(comms.unpack(swarm.packet_now())[1])
assert d[3] == 1 and d[5] == 2.0, d                    # contact: enemy quadrant, raw count
''', X03)


class RadioReservationTests(unittest.TestCase):
    def test_reserve_uses_idle_rays_then_food_only(self):
        run('''
out = radio.outgoing()
types = sorted(comms.unpack(v)[0] for v in out.values())
assert comms.T_DENSITY in types and comms.T_SWARM in types, types
# protect CROWN/PREY/PORTAL: fill all four rays with protected traffic
v = comms.crown_packet(3, 60, 5, w.RND)
full = {"N": v, "E": comms.portal_packet(1, 5, 6),
        "S": comms.crown_packet(4, 61, 5, w.RND, comms.T_PREY), "W": v}
out = radio._reserve(dict(full))
assert out["E"] == full["E"] and out["S"] == full["S"] # untouched
# a FOOD ray may be displaced
food = {"N": comms.food_packet([(60, w.RND)]), "E": v, "S": v, "W": v}
out = radio._reserve(dict(food))
assert comms.unpack(out["N"])[0] in (comms.T_DENSITY, comms.T_SWARM)
''', X03)


class FeatureV2Tests(unittest.TestCase):
    def test_global_feature_keys_and_units(self):
        run('''
for k in ("threat", "phase", "early", "sat", "area_here", "room_ratio",
          "counts", "lengths"):
    assert k in GF, k
assert GF["phase"] == w.RND / 500.0 and 0.0 <= GF["sat"] <= 1.0
assert GF["early"] is True and GF["area_here"] >= 1
assert len(GF["counts"]) == 3 and len(GF["lengths"]) == 3
''', X03)

    def test_previews_commit_nothing(self):
        run('''
cands, ctx = intentions.propose()
mem0 = dict(targets.MEM); trail0 = list(w.trail); body0 = list(w.body)
dens0 = dict(density.REPORTS); sw0 = dict(swarm.REPORTS)
gf = features.global_features(); tf = features.target_features(ctx)
for c in cands: features.preview(c, gf, tf)
assert dict(targets.MEM) == mem0
assert list(w.trail) == trail0 and list(w.body) == body0
assert dict(density.REPORTS) == dens0 and dict(swarm.REPORTS) == sw0
''', X03)


class PolicyP1Tests(unittest.TestCase):
    def test_strike_margin_relaxed_only_when_early_saturated_forager(self):
        run('''
w.occ[61] = (7, False, True); w.elen[7] = 3; w.UNITS = 5
w.LEN = 3; w.body = [58, 59, 60]
# even trade: gain 0. Calm margin 0.5 rejects it.
assert decision.strike_value(7, 1, P["atk_margin"]) is None
# relaxed margin admits the deliberate trade.
assert decision.strike_value(7, 1, P["atk_margin"] - P["aggro_relax"]) is not None
calm = {"early": False, "sat": 1.0}
assert not decision.aggression(calm)                   # late: no relaxation
hungry = {"early": True, "sat": 0.2}
assert not decision.aggression(hungry)                 # scarce team: no
hot = {"early": True, "sat": 0.9}
assert decision.aggression(hot)                        # early + saturated forager
roles.ROLE[0] = "crown"
assert not decision.aggression(hot)                    # the crown never pushes
''', X04)

    def test_confinement_scales_split_value(self):
        run('''
w.LEN = 6; w.body = [55, 56, 57, 58, 59, 60]; w.UNITS = 2
roles.ROLE[0] = "forager"
gf = dict(GF, sat=0.1)
pv_open = {"outcome": "split", "parent_area": 12, "pneed": 5, "child_room": 12,
           "threat_at_head": None, "threat_at_child": None}
pv_tight = dict(pv_open, parent_area=5, child_room=1)   # pneed met: no trap term
c_open = {"mode": "split", "arg": 2, "emergency": False, "preview": pv_open}
c_tight = {"mode": "split", "arg": 2, "emergency": False, "preview": pv_tight}
s_open = decision.score(c_open, {}, gf, {})
s_tight = decision.score(c_tight, {}, gf, {})
assert s_tight < s_open, (s_open, s_tight)             # confined: split less
base = P["split_val"] + P["split_sat_w"] * 0.4
assert abs(s_open - base) < 1e-9                       # open room: full value
assert s_tight > P["split_val"] * P["split_room_floor"]  # floored, not banned
''', X04)

    def test_progress_discounted_by_target_density(self):
        run('''
cand = {"mode": "move", "arg": [1], "exclusive": False, "emergency": False,
        "kind": "gather", "target": 71}
pv = {"outcome": "ok", "body_after": [59, 60, 61], "eaten": 0, "hit": None,
      "blind": 0, "steps": 1, "head_after": 61, "len_after": 3, "area": 24,
      "pocket": 0, "threat_at_head": None, "visits": 0, "flank": False,
      "prog": 1, "bed_block": False, "swarm_gain": 0.0}
cand["preview"] = pv
gf = dict(GF, early=False, sat=0.5)
tf_free = {"prog": [0]*4, "crown_flank": set(), "need": 5, "res_factor": 1.0}
tf_busy = dict(tf_free, res_factor=0.4)
s_free = decision.score(cand, tf_free, gf, {})
s_busy = decision.score(cand, tf_busy, gf, {})
assert s_busy < s_free and abs((s_free - s_busy) - P["w_goal"] * 0.6) < 1e-9
''', X04)


class ReconExecutorTests(unittest.TestCase):
    def _portal_setup(self):
        return '''
P["recon_min_area"] = 0    # the 11x11 test map is below the compact gate
w.seen[:] = [w.RND + 1] * w.NC          # everything seen: nothing to gather
w.sec_unseen[:] = [0] * len(w.sec_unseen)
# unpaired portal on the east edge of cell 61 (two steps from head 60)
k1 = w.ekey(61, 1)
w.ek[k1] = 3; w.epid[k1] = 5; w.pends[5] = [k1]
w.DC[61] = None; w.OPT[61] = None
targets.MEM["tval"] = 0.0
targets.MEM["target"] = -1
'''

    def test_recon_gating(self):
        run(self._portal_setup() + '''
w.LEN = 4; w.body = [57, 58, 59, 60]; w.UNITS = 6; w.BORN = 0
ctx = {"own_idx": {c: i for i, c in enumerate(w.body)}}
assert intentions.recon_portals(ctx) == [(61, 1, 5)]
w.LEN = 8; w.body = list(range(53, 61))              # too long to dive
assert intentions.recon_portals(ctx) == []
w.LEN = 4; w.body = [57, 58, 59, 60]
targets.MEM["tval"] = 5.0                            # food in reach: no recon
assert intentions.recon_portals(ctx) == []
targets.MEM["tval"] = 0.0
w.UNITS = 2                                          # team cannot spare a scout
assert intentions.recon_portals(ctx) == []
''', X05)

    def test_recon_candidate_is_an_objective_not_a_direction(self):
        run(self._portal_setup() + '''
P["recon_tval"] = 99.0   # in-range dives inflate tval; lift the gate for this probe
w.LEN = 4; w.body = [57, 58, 59, 60]; w.UNITS = 6; w.BORN = 0
cands, ctx = intentions.propose()
rec = [c for c in cands if c["mode"] == "recon"]
assert len(rec) == 1
c = rec[0]
assert c["kind"] == "scout" and c["target"] == 61 and isinstance(c["arg"], int)
''', X05)

    def test_executor_self_routes_and_scores(self):
        run(self._portal_setup() + '''
P["recon_tval"] = 99.0
w.LEN = 4; w.body = [57, 58, 59, 60]; w.UNITS = 6; w.BORN = 0
cands, ctx = intentions.propose()
rec = [c for c in cands if c["mode"] == "recon"][0]
rp = executors.preview_recon(rec)
assert rp["available"] and rp["steps"] == 2 and not rp["dive"], rp
s = decision.score(rec, {"prog": [0]*4, "crown_flank": set(), "need": 5},
                   GF["threat"])
assert s > 0.0, s                                    # recon beats nothing-to-do
rec["score"] = s
r = executors.execute(rec)
assert r["command"][0] == "move" and r["status"] == "active"
assert r["reason"] == "portal-approach", r
# step onto the portal cell: now the dive itself is the route
w.HEAD = 61; w.body = [58, 59, 60, 61]
rec["recon_preview"] = None
rp2 = executors.preview_recon(rec)
assert rp2["available"] and rp2["dive"], rp2
r2 = executors.execute(rec)
assert r2["predicted"] == "dive" and r2["status"] == "completed"
assert r2["reason"] == "portal-dive"
''', X05)

    def test_recon_unavailable_when_blocked(self):
        run(self._portal_setup() + '''
w.LEN = 4; w.body = [57, 58, 59, 60]; w.UNITS = 6; w.BORN = 0
w.occ[50] = (9, False, False)   # wall off the only corridor cells
w.occ[61] = (9, False, False)   # the portal cell itself is occupied
w.occ[71] = (9, False, False)
w.occ[49] = (9, False, False)
cand = {"mode": "recon", "target": 61, "pid": 5, "score": 1.0, "kind": "scout"}
rp = executors.preview_recon(cand)
assert not rp["available"], rp
cand["recon_preview"] = rp
r = executors.execute(cand)
assert r["status"] == "fallback" and r["reason"] == "recon-route-unavailable"
assert r["command"][0] == "move"                       # still a legal command
''', X05)


class GenerationContractTests(unittest.TestCase):
    def test_executor_menu_and_record_interface(self):
        for bot in (X03, X04, X05):
            run('''
assert set(executors.EXECUTORS) == set(intentions.KINDS)
cands, ctx = intentions.propose()
gf = features.global_features(); tf = features.target_features(ctx)
for c in cands: features.preview(c, gf, tf)
try:
    sel, ranked = decision.choose(cands, tf, gf)
except TypeError:
    sel, ranked = decision.choose(cands, tf, gf["threat"])
rec = executors.execute(sel)
for k in ("command", "predicted", "status", "reason", "trade",
          "path_cells", "report", "diag"):
    assert k in rec, (k, rec)
''', bot)

    def test_traces_stay_disabled_in_deployment(self):
        for bot in (X03, X04, X05):
            run('''
assert P["intent_trace"] == 0 and P["training_trace"] == 0
assert P.get("density_trace", 0) == 0
''', bot)

    def test_protocol_is_unmodified_bahamut_adapter(self):
        ref = (ROOT / 'examples/bahamut-scaffold/protocol.py').read_bytes()
        for bot in (X03, X04, X05):
            self.assertEqual((bot / 'protocol.py').read_bytes(), ref)


if __name__ == '__main__':
    unittest.main()
