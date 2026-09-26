#!/usr/bin/env python3
"""F1 unit checks: T_MASS type-7 packet discipline in build/feynman/dev.

Covers: roundtrip/saturation/rejects, tag+checksum rejection of foreign or
corrupted payloads, hear() dedup/TTL/self rules, schedule() ray discipline
(idle-first, food displacement only, crown/prey never displaced), the F1
relay switch, and the sender-id aliasing guard. Run from the repo root:

  .venv/bin/python tools/feynman/test_f1.py
"""
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "build" / "feynman" / "dev"))

# ---- stub world -------------------------------------------------------------
w = types.ModuleType("world")
w.W, w.H = 30, 30
w.TEAM = "A"
w.RND = 100
w.ME = 7
w.HEAD = 5 + 5 * 30
w.LEN = 6
w.alen = {11: 4, 12: 3}
w.elen = {21: 9}
w.enemy_heads = [(8 + 6 * 30, 21)]
w.DIRS = ["N", "E", "S", "W"]


def tdist(a, b):
    ax, ay, bx, by = a % w.W, a // w.W, b % w.W, b // w.W
    dx = abs(ax - bx)
    dy = abs(ay - by)
    return min(dx, w.W - dx) + min(dy, w.H - dy)


w.tdist = tdist
sys.modules["world"] = w

import comms
import mass

FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


# ---- packet roundtrip -------------------------------------------------------
pkt = comms.mass_packet(7, 10.4, 20.6, 13.2, 9.0, 100)
typ, payload = comms.unpack(pkt)
check("roundtrip type", typ == comms.T_MASS)
check("roundtrip fields", comms.mass_decode(payload) == (7, 10, 21, 13.0, 9.0, 100))

big = comms.mass_packet(7, 1, 1, 500.0, 300.0, 100)
check("lengths saturate at 127", comms.mass_decode(comms.unpack(big)[1])[3:] == (127.0, 127.0, 100))

check("future round rejected at pack", comms.mass_packet(7, 1, 1, 5, 5, 500) is None)
w.RND = 50
stale = comms.mass_packet(7, 1, 1, 5, 5, 100)
check("decode rejects report from the future", comms.mass_decode(comms.unpack(stale)[1]) is None)
w.RND = 100

# ---- tag + checksum reject foreign/corrupted payloads -----------------------
rejects = 0
for flip in range(64):
    if comms.unpack(pkt ^ (1 << flip)) is None:
        rejects += 1
check("single-bit corruption rejected in >= 60/64 cases", rejects >= 60)
check("foreign tag rejected", comms.unpack((pkt & ~0xFF) | 0x00) is None)

# ---- hear() discipline ------------------------------------------------------
mass.REPORTS.clear()
mass.init()
rep = (5, 10, 10, 20.0, 8.0, 99)
mass.hear(rep, pkt)
check("accept fresh report", 5 in mass.REPORTS)
mass.hear((5, 12, 12, 20.0, 8.0, 98), pkt)
check("older round from same sender rejected", mass.REPORTS[5][:2] == (10, 10))
mass.hear((5, 12, 12, 20.0, 8.0, 100), pkt)
check("newer round accepted", mass.REPORTS[5][:2] == (12, 12))
mass.hear((w.ME & 511, 1, 1, 2.0, 2.0, 100), pkt)
check("own id never stored", (w.ME & 511) not in mass.REPORTS)
mass.hear((9, 1, 1, 2.0, 2.0, 100 - mass.TTL - 1), pkt)
check("expired report rejected", 9 not in mass.REPORTS)

# ---- schedule() ray discipline ----------------------------------------------
mass.LOCAL = (10.0, 10.0, 15.0, 6.0, 100)
mass.REPORTS.clear()
mass.REPORTS[5] = (12, 12, 20.0, 8.0, 100, pkt)
w.RND = 101  # (RND + ME) % mass_period == 0 for period 1

crown = comms.crown_packet(3, 100, 12, 99)
legacy = {"N": crown, "E": comms.food_packet([(50, 90)])}
P = mass.P
P["mass_rays"] = 1
P["mass_relay"] = 1
out = mass.schedule(legacy)
check("crown ray never displaced", out["N"] == crown)
check("one mass ray added on idle ray", sum(1 for v in out.values() if v != crown and comms.unpack(v)[0] == comms.T_MASS) >= 1)

full = {"N": crown, "E": comms.food_packet([(50, 90)]), "S": comms.food_packet([(60, 90)]), "W": comms.food_packet([(70, 90)])}
out = mass.schedule(full)
foods = sum(1 for v in out.values() if comms.unpack(v) and comms.unpack(v)[0] == comms.T_FOOD)
check("displaces one food ray when no idle ray", foods == 2)

P["mass_rays"] = 2
w.RND = 101  # odd round: relay turn when mass_relay=1
out = mass.schedule(dict(full))
mass_pkts = [v for v in out.values() if comms.unpack(v) and comms.unpack(v)[0] == comms.T_MASS]
check("relay on: second ray relays peer packet unchanged", len(mass_pkts) == 2 and pkt in mass_pkts)
P["mass_relay"] = 0
out = mass.schedule(dict(full))
mass_pkts = [v for v in out.values() if comms.unpack(v) and comms.unpack(v)[0] == comms.T_MASS]
check("relay off: no relayed peer packet", pkt not in mass_pkts and len(mass_pkts) == 2)

P["mass_rays"] = 1
w.ME = 600
before = dict(full)
out = mass.schedule(full)
check("sender id >= 512 never aliases", out == before)
w.ME = 7

P["mass_rays"] = 0
out = mass.schedule(dict(full))
check("mass_rays=0 leaves legacy untouched (x01 parity)", out == before)

print()
if FAIL:
    print("FAILED:", *FAIL)
    sys.exit(1)
print("all F1 checks passed")
