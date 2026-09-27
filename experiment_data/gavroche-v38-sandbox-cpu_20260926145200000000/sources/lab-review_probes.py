"""Reproducers for review findings. Imports read-only sources into isolated state."""
import gc
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from lab import ROOT, source_hashes

OUT = ROOT / 'build/lineage-review-20260924/probes'
OUT.mkdir(parents=True, exist_ok=True)
SNAPSHOT = ROOT / 'build/lineage-review-20260924/flagship/sources'


def load(name, folder):
    spec = importlib.util.spec_from_file_location(name, SNAPSHOT / 'bots' / folder / 'main.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


findings = []
k = load('review_kraken', 'kraken-v04-eval')
k.W = k.H = 32
k.setup()
k.my_len, k.units, k.round_now, k.boot_done = 4, 1, 100, True
safe, threatened = k.want_split(0), k.want_split(2)
assert (safe, threatened) == (2, 2)
findings.append(dict(id='K1', observation='Kraken proposes SPLIT 2 with either safe or lethal-risk head; danger_here is unused.', values=[safe, threatened]))
k.pends = {1: [100], 257: [200]}
p1, p257 = k.portal_payload(1), k.portal_payload(257)
k.pends, k.epid = {}, {}
k.apply_packet(k.K_PORTAL, p1)
k.apply_packet(k.K_PORTAL, p257)
assert k.pends[1] == [100, 200]
findings.append(dict(id='K2', observation='Distinct portal IDs 1 and 257 become one false pair after gossip decoding.', decoded_pairs=k.pends))

k.my_id, k.head, k.my_len, k.role = 1, 100, 3, 2
status1 = k.self_payload()
k.my_id = 257
assert k.self_payload() == status1
findings.append(dict(id='K3', observation='Kraken self-report IDs 1 and 257 encode identically (eight-bit identity).', payload=status1))
k.setup()
k.ek = bytearray([1]) * (2 * k.NC)
k.head = 60
k.emit_move([1])
k.send_sonar()
assert k.radar[0] == 60 and k.trail[-1] == 61
findings.append(dict(id='K4', observation='After moving east from 60 to 61, sonar radar origin remains 60. Sonar is cast after the action, so echo reconstruction uses the wrong origin.', stored_origin=k.radar[0], actual_post_move_head=k.trail[-1]))

o = load('review_ouro', 'ouroboros-v05-spread')
o.W = o.H = 32
o.setup()
o.RND, o.LEN, o.HEAD = 100, 3, 60
o.ek = bytearray([1]) * (2 * o.NC)
o.occ = {}
o.pearls = {61: 90}  # stale; no current observation at destination
res = o.simulate([1, 1], [58, 59, 60])
assert res[0] and res[2] == 3 and res[3] == 1
findings.append(dict(id='O1', observation='Two-step simulation counts a stale pearl as present: predicts final length 3 instead of 2 if it is gone. Candidate length cap separately prevents relying on it for sprint payment.', predicted_length=res[2], predicted_pearls=res[3]))
o.setup()
o.pends = {1: [100, 110], 257: [200, 210]}
a, b = o.portal_packet(1), o.portal_packet(257)
o.pends, o.epid = {}, {}
o.hear(a)
o.hear(b)
o.learn(200, '257')
assert o.epid[200] == 1  # direct observation cannot repair gossip ID
findings.append(dict(id='O2', observation='Portal IDs 1/257 alias on radio; learn() ignores direct correction once edge kind is portal.', observed_real_id=257, retained_id=o.epid[200], pairs=o.pends))
o.ROLE, o.RND, o.LEN, o.UNITS, o.HEAD = o.GATHER, 200, 4, 20, 60
o.decide = lambda: ((0.0, [1], 'move'), -1)
o.commit_path = lambda path: None
o.send_sonars = lambda *args: None
o.take_turn()
first_role = o.ROLE
o.RND = 201
o.allies[999] = (100, 40, o.CROWN, 201)
o.take_turn()
assert first_role == o.CROWN and o.ROLE == o.CROWN
findings.append(dict(id='O3', observation='A length-4 dragon with no heard crown crowns itself at round 200, then stays crown after hearing a length-40 crown.', roles=[first_role,o.ROLE]))
gc.enable()

sys.path.insert(0, str(ROOT / 'tools/leviathan'))
from test_lab import board
assert source_hashes(ROOT / 'bots/leviathan-v07-local-cache') == source_hashes(SNAPSHOT / 'bots/leviathan-v07-local-cache')
x, y = board(), board()
y.reports = {i: (61, 100, y.round) for i in range(20)}
action1, action2 = x.decide()[0], y.decide()[0]
assert action1 == action2
findings.append(dict(id='L1', observation='Injecting fresh teammate reports has no decision effect; reports are stored but not consumed by evaluation.', actions=[action1,action2]))
b = board()
b.body, b.length, b.own, b.round, b.units = [60,59,58,57], 4, {60,59,58,57}, 450, 1
late, indicator = b.decide()
assert late == 'SPLIT 2'
findings.append(dict(id='L2', observation='A safe length-4 lone gatherer still splits at round 450: late split penalty is soft, not a freeze.', action=late, indicator=indicator))

source = (SNAPSHOT / 'bots/hydra-v06-echo/hunter.cpp').read_text()
source = source.replace('class Bot {', 'class Bot {\npublic:', 1).replace('int main() {','int hydra_original_main() {',1)
source += '\nint main() { auto a = Bot::team_status_message(1,4,12,13); auto b = Bot::team_status_message(65,4,12,13); std::cout << a << " " << b << "\\n"; return a != b; }\n'
cpp, exe = OUT / 'hydra_status_probe.cpp', OUT / 'hydra_status_probe'
cpp.write_text(source)
subprocess.run(['clang++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True,capture_output=True)
run = subprocess.run([str(exe)],check=True,capture_output=True,text=True)
findings.append(dict(id='H1', observation='Actual Hydra status encoder gives identical packets to dragon IDs 1 and 65.', output=run.stdout.strip()))

portal_ranges = {}
for path in (ROOT / 'maps').glob('*.map'):
    ids = [int(p[3]) for line in path.read_text().splitlines() if (p := line.split()) and p[0]=='EDGE' and len(p)>=4 and int(p[3])>=0]
    if ids and max(ids) > 255:
        portal_ranges[path.name] = dict(max_id=max(ids), distinct_ids=len(set(ids)))
findings.append(dict(id='M1', observation='Bundled maps where 8-bit portal IDs are insufficient.', maps=portal_ranges))
(OUT / 'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
print(json.dumps(findings,indent=2))
