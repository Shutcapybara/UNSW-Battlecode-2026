"""TT: scaffold a structured mimic of a top team from hb1-04-deployable (the Heartbreaker mimic), with the changes the
top teams need. Models are written into the new directory afterwards by the exporters.

    .venv/bin/python tools/tt/make_mimic.py NAME TEAM_LABEL

Changes to hb1-04's Mimic (hb1_policy.hpp):
  - a self-kill (cull) model runs first: p >= 0.5 -> step backward into the own neck (certain death; the outcome of
    both top teams' self-kill methods - an invalid command or a backward step);
  - Heartbreaker's W2 fallback (step into an ally head) is replaced by dying in place when trapped with no legal
    split (forgot to mention 98 %, Cache me outside 70 % of such turns);
  - sonar emits one ray per direction set in the predicted mask (relative to the pre-move facing), instead of
    Heartbreaker's four rays with a redrawn slot.
"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
name, label = sys.argv[1], sys.argv[2]
d = ROOT / 'bots' / name
if d.exists():
    shutil.rmtree(d)
shutil.copytree(ROOT / 'bots/hb1-04-deployable', d, ignore=shutil.ignore_patterns('.unswbc-build'))
p = d / 'hb1_policy.hpp'; s = p.read_text()
s = s.replace('    Bound gate{gate_model}, alloc{alloc_model}, dir{dirc_bind}, sonar{sonar_model};',
              '    Bound gate{gate_model}, alloc{alloc_model}, dir{dirc_bind}, sonar{sonar_model}, cull{cull_model};')
old = '''        if (exitless && elig) {                                           // W1
            c.split = true; c.child = child_size(r, L); c.why = '1';
            return c;
        }
        if (exitless) {                                                   // W2
            c.rel = 'F'; c.why = '2';
            for (char rel : {'L', 'R', 'F'})
                if (r.get(std::string("c") + rel + "_block") == 5) c.rel = rel;
            return c;
        }'''
new = '''        if (proba(cull_model, cull.vec(r))[1] >= 0.5) {                 // TT: the team's learned self-kill
            c.rel = 'B'; c.why = 'x';
            return c;
        }
        if (exitless && elig) {                                           // W1
            c.split = true; c.child = child_size(r, L); c.why = '1';
            return c;
        }
        if (exitless) {                                                   // TT: trapped, no legal split - die in place
            c.rel = 'B'; c.why = 'X';
            return c;
        }'''
assert s.count(old) == 1
s = s.replace(old, new)
a = s.index('    std::vector<char> sonar_dirs(Row const& r, Choice const& c, char facing) {')
b = s.index('        return rays;\n    }\n', a) + len('        return rays;\n    }\n')
s = s[:a] + '''    // TT: one ray per direction set in the predicted mask (relative to the pre-move facing), payload 0.
    std::vector<char> sonar_dirs(Row const& r, Choice const& c, char facing) {
        Row s = r;
        s.set("act_F", !c.split && c.rel == 'F'); s.set("act_R", !c.split && c.rel == 'R');
        s.set("act_L", !c.split && c.rel == 'L'); s.set("act_split", c.split);
        auto p = proba(sonar_model, sonar.vec(s));
        int best = 0;
        for (int i = 1; i < sonar_model.n_class; i++) if (p[i] > p[best]) best = i;
        int const mask = sonar_model.classes[best];
        static constexpr char RB[4] = {'F', 'R', 'B', 'L'};
        std::vector<char> rays;
        for (int bit = 0; bit < 4; bit++)
            if (mask & (1 << bit)) rays.push_back(rel_to_abs(facing, RB[bit]));
        return rays;
    }
''' + s[b:]
p.write_text(s)
p = d / 'CANDIDATE.toml'; t = p.read_text()
t = t.replace('name = "hb1-04-deployable"', f'name = "{name}"').replace('lineage = "hb1"', 'lineage = "tt"').replace('author = "claude/hb1"', 'author = "claude/tt"').replace('lineage_parent = "hb1-03-direction-scaled"', 'lineage_parent = "hb1-04-deployable"')
t = re.sub(r'hypothesis = ".*?"\n', f'hypothesis = "A structured mimic of {label}: the HB-1 recipe (v5 features in C++, exported GBTs) with the top teams\' self-kill as a learned decision and their trapped-state behaviour."\n', t)
t = re.sub(r'mechanism = ".*?"\n', f'mechanism = "{label}\'s own models (gate, child size, sonar mask, self-kill, scaled direction) on hb1-04\'s mimic chassis; cull model first, die in place when trapped with no legal split, one sonar ray per mask bit."\n', t)
t = re.sub(r'expected_change = ".*?"\n', f'expected_change = "Fidelity and strength comparable to {label}; LOCAL ONLY (the full direction model exceeds the 4 MiB upload zip)."\n', t)
t = t.replace('status = "candidate packaging (not registered)"', 'status = "local-only mimic"')
p.write_text(t)
print('scaffolded', d)
