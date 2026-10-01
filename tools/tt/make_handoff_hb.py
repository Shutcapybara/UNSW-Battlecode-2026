"""TT: a top-team mimic that hands each dragon to hb1-14 (Ares V06 + Heartbreaker's direction prior) at a fixed round.

    .venv/bin/python tools/tt/make_handoff_hb.py NAME HANDOFF_BOT

HANDOFF_BOT is a tools/tt/make_handoff.py bot (mimic before handoff_round, Ares V06 after). This swaps its Ares half
for hb1-14-prior-r540's policy and keeps both direction models: the mimic's as hb1::dirc_*, Heartbreaker's renamed
hb1::dirhb_* (hb1_direction_compact_hb.hpp). The mimic's v5 feature process keeps running after the switch and feeds
the prior, as hb1-14's own main does. Local only.
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
name, src = sys.argv[1], sys.argv[2]
HB = ROOT / 'bots' / 'hb1-14-prior-r540'
d = ROOT / 'bots' / name
if d.exists():
    shutil.rmtree(d)
shutil.copytree(ROOT / 'bots' / src, d, ignore=shutil.ignore_patterns('.unswbc-build'))

ren = lambda s: re.sub(r'\bdirc_', 'dirhb_', s)
(d / 'hb1_direction_compact_hb.hpp').write_text(ren((HB / 'hb1_direction_compact.hpp').read_text()))
c = ren((HB / 'hb1_compact.hpp').read_text()).replace('"hb1_direction_compact.hpp"', '"hb1_direction_compact_hb.hpp"')
c = c.replace('"direction_v04"', '"direction_hb"')
(d / 'hb1_compact_hb.hpp').write_text(c)

s = (HB / 'policy.hpp').read_text()
a, b = s.index('namespace hb1 {'), s.index('}  // namespace hb1') + len('}  // namespace hb1')
s = s[:a] + '// (hb1::block_from comes from hb1_policy.hpp in this bot)' + s[b:]
s = s.replace('#include "hb1_compact.hpp"', '#include "hb1_compact_hb.hpp"')
for x in ('dirc_bind', 'dirc_proba', 'dirc_classes'):
    assert x in s
    s = s.replace('hb1::' + x, 'hb1::' + x.replace('dirc_', 'dirhb_'))
assert 'dirc_' not in s
(d / 'policy.hpp').write_text(s)

p = d / 'params.hpp'; s = p.read_text()
hbp = (HB / 'params.hpp').read_text()
m = re.search(r'\n(    // HB-1 Q5 \(hb1-12\).*?static constexpr double hb1_dir_lambda = [0-9.]+;)', hbp, re.S)
anchor = '    static constexpr bool hb1_mode = true;'
assert m and s.count(anchor) == 1
s = s.replace(anchor, m.group(1) + '\n' + anchor)
p.write_text(s)
assert (d / 'params.hpp').read_text().count('hb1_dir_lambda') == 1

p = d / 'main.cpp'; s = p.read_text()
reps = [
    ('        ares::Decision dec;\n        bool ok = true;',
     '''        ares::Decision dec;
        // hb1-14: this turn's v5 row (the mimic's feature process) as the policy's Heartbreaker prior.
        char const hb_facing = ct.get_dir().value;
        hb1::Row hb_row;
        pol.hb_row = nullptr;
        try {
            hb_row = mim.proc.features(hb1::block_from(ct, game));
            pol.hb_row = &hb_row;
        } catch (...) {
        }
        bool ok = true;'''),
    ('''        if (dec.act == ares::Act::SPLIT) {
            ct.do_split(dec.split);''',
     '''        if (dec.act == ares::Act::SPLIT) {
            mim.proc.record_split(dec.split);
        } else if (!dec.dirs.empty()) {
            std::string rels;
            char f = hb_facing;
            for (int dd : dec.dirs) { char a = ares::dir_char(dd); rels += hb1::abs_to_rel(f, a); f = a; }
            mim.proc.record_move(rels);
        }
        if (dec.act == ares::Act::SPLIT) {
            ct.do_split(dec.split);'''),
]
for a_, b_ in reps:
    assert s.count(a_) == 1, a_[:50]
    s = s.replace(a_, b_)
p.write_text(s)
c = d / 'CANDIDATE.toml'
if c.exists():
    c.write_text(c.read_text().replace(src, name) + '\n# TT handoff to hb1-14 (Ares V06 + Heartbreaker direction prior) instead of plain V06.\n')
print('wrote', d)
