"""TT: a bot that hands the one decision where hb1-14 and tt-05 differ - when a dragon starts feeding the crown -
from hb1-14 (feed_base 40, ~r400) to tt-05 (feed_base 140, ~r300) as the game progresses.

    .venv/bin/python tools/tt/make_ramp.py NAME RAMP_FROM RAMP_TO

hb1-14 and tt-05 are the same bot except for that onset. Each dragon, each turn, uses tt-05's onset with probability
rising linearly 0 -> 1 from RAMP_FROM to RAMP_TO (deterministic per dragon and round, so both uses in a turn agree),
hb1-14's otherwise. Built on hb1-14-prior-r540: uploadable.
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
name, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d = ROOT / 'bots' / name
if d.exists():
    shutil.rmtree(d)
shutil.copytree(ROOT / 'bots/hb1-14-prior-r540', d, ignore=shutil.ignore_patterns('.unswbc-build'))
p = d / 'params.hpp'; s = p.read_text()
old = '    static constexpr int feed_base = 40;'
assert s.count(old) == 1
s = s.replace(old, f'''    static constexpr int feed_base = 40;          // hb1-14's feeding onset (~r400 on a 60x40 map)
    // TT ramp: tt-05's onset (feed_base 140, ~r300) is used with probability rising 0 -> 1 from ramp_from to ramp_to.
    static constexpr int feed_base_tt = 140;
    static constexpr int ramp_from = {r0};
    static constexpr int ramp_to = {r1};''')
p.write_text(s)
p = d / 'policy.hpp'; s = p.read_text()
line = '        int feed_from = 500 - Params::feed_base - static_cast<int>((w.W + w.H) * Params::feed_k);'
line2 = '            int feed_from = 500 - Params::feed_base - static_cast<int>((w.W + w.H) * Params::feed_k);'
assert s.count(line2) == 1 and s.count(line) == 2            # line is a substring of line2 (indentation)
s = s.replace(line2, '            int feed_from = feed_from_ramp(w);')
s = s.replace(line, '        int feed_from = feed_from_ramp(w);')
assert s.count('feed_from_ramp(w)') == 2
helper = '''    // TT ramp: hb1-14's feeding onset early in the handoff window, tt-05's late; per dragon and round.
    int feed_from_ramp(const World& w) const {
        int const span = static_cast<int>((w.W + w.H) * Params::feed_k);
        int const hb = 500 - Params::feed_base - span, tt = 500 - Params::feed_base_tt - span;
        double const p = w.rnd < Params::ramp_from ? 0.0 : w.rnd >= Params::ramp_to ? 1.0
            : double(w.rnd - Params::ramp_from) / double(Params::ramp_to - Params::ramp_from);
        std::uint64_t h = std::uint64_t(w.me) * 0x9E3779B97F4A7C15ull ^ std::uint64_t(w.rnd) * 0xD1B54A32D192ED03ull;
        h ^= h >> 31; h *= 0x94D049BB133111EBull; h ^= h >> 29;
        return double(h >> 11) * 0x1.0p-53 < p ? tt : hb;
    }

    double lv_now(const World& w) const {'''
assert s.count('    double lv_now(const World& w) const {') == 1
s = s.replace('    double lv_now(const World& w) const {', helper)
p.write_text(s)
p = d / 'CANDIDATE.toml'; s = p.read_text()
s = s.replace('name = "hb1-14-prior-r540"', f'name = "{name}"').replace('lineage = "hb1"', 'lineage = "tt"').replace('author = "claude/hb1"', 'author = "claude/tt"').replace('lineage_parent = "hb1-12-direction-prior"', 'lineage_parent = "hb1-14-prior-r540"')
s = re.sub(r'hypothesis = ".*?"\n', 'hypothesis = "hb1-14 (Heartbreaker direction prior on Ares) and tt-05 (the same bot feeding the crown from ~r300, the top teams\' timing) tie on the z1 panel (141-19) with different endgames. Handing the feeding decision from hb1-14 to tt-05 gradually through the game converts more smoothly than either fixed onset."\n', s)
s = re.sub(r'mechanism = ".*?"\n', f'mechanism = "One helper vs hb1-14: each dragon, each turn, uses tt-05\'s feeding onset (feed_base 140) with probability rising linearly 0 -> 1 from r{r0} to r{r1}, hb1-14\'s (40) otherwise. Everything else identical to hb1-14 (and tt-05)."\n', s)
s = re.sub(r'expected_change = ".*?"\n', 'expected_change = "Longest dragon and round-limit record between or above hb1-14 and tt-05, with fewer lost eliminations than tt-05. Uploadable (same size as hb1-14)."\n', s)
p.write_text(s)
print('built', d)
