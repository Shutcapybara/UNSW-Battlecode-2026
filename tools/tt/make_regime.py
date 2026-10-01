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
name, fb = sys.argv[1], int(sys.argv[2])
base = sys.argv[3] if len(sys.argv) > 3 else 'hb1-17-prior-lam20'
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
    static constexpr int regime_area = 1100;          // W * H at or above: large map
    static constexpr double regime_portals = 4.0;     // portal edges per 100 seen cells at or above: portal-dense
    static constexpr int regime_min_seen = 64;''')
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
        return 100.0 * portals / w.seen_count >= Params::regime_portals;
    }
    int feed_from_regime(const World& w) const {
        int const base = limit_regime(w) ? Params::feed_base_limit : Params::feed_base;
        return 500 - base - static_cast<int>((w.W + w.H) * Params::feed_k);
    }

    double lv_now(const World& w) const {'''
assert s.count('    double lv_now(const World& w) const {') == 1
s = s.replace('    double lv_now(const World& w) const {', helper)
p.write_text(s)
p = d / 'CANDIDATE.toml'
if p.exists():
    s = p.read_text().replace(base, name)
    p.write_text(s + f'\n# TT regime selector: feed_base {fb} on large (W*H>=1100) or portal-dense (>=4 portal edges per 100 seen cells) maps, base {base} otherwise.\n')
print('built', d)
