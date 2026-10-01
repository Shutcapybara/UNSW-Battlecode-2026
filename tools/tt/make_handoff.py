"""TT: a mimic that hands each dragon to Ares V06 at a fixed round - the top team's swarm early, Ares' crown election
and feeding (the conversion the mimics lack) late.

    .venv/bin/python tools/tt/make_handoff.py NAME MIMIC_BOT HANDOFF_ROUND

Copies MIMIC_BOT (a tools/tt/make_mimic.py bot: hb1_mode on the Ares V06 chassis). Ares' World is sensed every turn
and the mimic's moves are committed to it, so the map memory is complete at the switch; the Ares Policy starts at
HANDOFF_ROUND (all dragons switch on the same round). Local only when MIMIC_BOT is.
"""
import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
name, src, rnd = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = ROOT / 'bots' / name
if d.exists():
    shutil.rmtree(d)
shutil.copytree(ROOT / 'bots' / src, d, ignore=shutil.ignore_patterns('.unswbc-build'))
p = d / 'params.hpp'; s = p.read_text()
old = '    static constexpr bool hb1_mode = true;'
assert s.count(old) == 1
s = s.replace(old, old + f'''
    // TT handoff: the mimic decides before this round, the Ares policy from it (World is sensed throughout).
    static constexpr int handoff_round = {rnd};''')
p.write_text(s)
p = d / 'main.cpp'; s = p.read_text()
reps = [
    ('    while (unswbc::update(ct, game)) {\n        if (ares::Params::hb1_mode) {',
     '''    while (unswbc::update(ct, game)) {
        bool sensed = true;
        try {
            w.sense(ct, game);
        } catch (...) {
            sensed = false;
        }
        if (ares::Params::hb1_mode && (!sensed || w.rnd < ares::Params::handoff_round)) {'''),
    ('''                std::cout << "MOVE " << hb1::rel_to_abs(facing, ch.rel) << "\\n";
                mim.proc.record_move(std::string(1, ch.rel));''',
     '''                char const a = hb1::rel_to_abs(facing, ch.rel);
                std::cout << "MOVE " << a << "\\n";
                mim.proc.record_move(std::string(1, ch.rel));
                if (sensed && ch.rel != 'B') {
                    try { w.commit_move({ares::dir_index(unswbc::Direction{a})}); } catch (...) {}
                }'''),
    ('''        try {
            w.sense(ct, game);
            if (ARES_MEASURE == 2) {''', '''        try {
            if (ARES_MEASURE == 2) {'''),
]
for a, b in reps:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
p.write_text(s)
c = d / 'CANDIDATE.toml'
if c.exists():
    c.write_text(c.read_text().replace(src, name) + f'\n# TT handoff: {src} before round {rnd}, Ares V06 policy from it.\n')
print('wrote', d)
