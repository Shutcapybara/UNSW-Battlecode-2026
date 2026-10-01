"""TT: map-regime selector - an earlier feeding onset only where local features say the game will go to the round limit.

    .venv/bin/python tools/tt/make_regime.py NAME FEED_BASE_LIMIT [BASE_BOT]      (BASE_BOT default hb1-17-prior-lam20)

Ladder per-map analysis (tools/tt/map_specialists.py, map_mechanism.py): games on large maps and portal-dense maps
end at the round limit (top teams eliminate in 0-21 % of games there), where the longest dragon decides; games on
the small maps end by elimination. Our bots lose the round-limit maps on length, often with a material lead; feeding
the crown earlier (tt-05, feed_base 140) fixes that there but costs a little on elimination maps. So: use
feed_base FEED_BASE_LIMIT when
  W * H >= regime_area (1100)                                  - known at init, or
  portal edges seen / cells seen >= regime_portals (4 per 100) - with at least 64 cells seen,
and the base bot's feed_base otherwise. No map names. Uploadable when BASE_BOT is.
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('name'); ap.add_argument('feed_base_limit', type=int); ap.add_argument('base', nargs='?', default='hb1-17-prior-lam20')
ap.add_argument('--area', type=int, default=1100, help='W*H threshold; 0 disables the size rule')
ap.add_argument('--portals', type=float, default=4.0, help='portal edges per 100 seen cells')
ap.add_argument("--min-seen", type=int, default=64, help="cells seen before the portal rule may fire")
ap.add_argument("--per-area", action="store_true", help="portal edges per 100 map cells (W*H), not per 100 seen cells: only grows with exploration, so local clusters cannot trip it")
a = ap.parse_args()
name, fb, base = a.name, a.feed_base_limit, a.base
area = a.area if a.area > 0 else 1 << 30
d = ROOT / 'bots' / name
if d.exists():
    shutil.rmtree(d)
shutil.copytree(ROOT / 'bots' / base, d, ignore=shutil.ignore_patterns('.unswbc-build'))
p = d / 'params.hpp'; s = p.read_text()
old = '    static constexpr int feed_base = 40;'
assert s.count(old) == 1
s = s.replace(old, f'''    static constexpr int feed_base = 40;
    // TT regime selector: feeding onset on maps whose local features predict a round-limit game.
    static constexpr int feed_base_limit = {fb};
    static constexpr int regime_area = {area};          // W * H at or above: large map
    static constexpr double regime_portals = {a.portals};     // portal edges per 100 seen cells at or above: portal-dense
    static constexpr int regime_min_seen = {a.min_seen};''')
p.write_text(s)
p = d / 'policy.hpp'; s = p.read_text()
line = 'int feed_from = 500 - Params::feed_base - static_cast<int>((w.W + w.H) * Params::feed_k);'
assert s.count(line) == 2
s = s.replace(line, 'int feed_from = feed_from_regime(w);')
helper = '''    // TT regime selector: large or portal-dense maps go to the round limit; feed the crown earlier there.
    bool limit_regime(const World& w) const {
        if (w.W * w.H >= Params::regime_area) return true;
        if (w.seen_count < Params::regime_min_seen) return false;
        int portals = 0;
        for (uint8_t k : w.ek) portals += k == EK_PORTAL;
        return 100.0 * portals / DENOM >= Params::regime_portals;
    }
    int feed_from_regime(const World& w) const {
        int const base = limit_regime(w) ? Params::feed_base_limit : Params::feed_base;
        return 500 - base - static_cast<int>((w.W + w.H) * Params::feed_k);
    }

    double lv_now(const World& w) const {'''
helper = helper.replace('DENOM', '(w.W * w.H)' if a.per_area else 'w.seen_count')
assert s.count('    double lv_now(const World& w) const {') == 1
s = s.replace('    double lv_now(const World& w) const {', helper)
p.write_text(s)
p = d / 'CANDIDATE.toml'
if p.exists():
    s = p.read_text().replace(base, name)
    p.write_text(s + f'\n# TT regime selector: feed_base {fb} on large (W*H>={area}) or portal-dense (>={a.portals} portal edges per 100 seen cells) maps, base {base} otherwise.\n')
print('built', d)
