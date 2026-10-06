"""Use keeper imitation only as a normal queen-production split prior."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
src=root/'bots/kenma-08-lossless-direction';dst=root/'bots/kenma-22-keeper-split-prior'
assert not dst.exists();shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
for file in ['gbt_compact.hpp','kenma_queen_model.hpp']:shutil.copy2(root/'bots/kenma-04-keeper-action'/file,dst/file)
(dst/'kenma_split_prior.hpp').write_text(r'''// Split-vs-move likelihood only; parent movement ranking remains unchanged.
#pragma once
#include <algorithm>
#include <cmath>
#include "gbt_compact.hpp"
#include "kenma_queen_model.hpp"
namespace kenma {
inline double split_log_odds(double const* p){
    double move=p[0]+p[1]+p[2]+p[3],split=p[4]+p[5]+p[6];
    double z=std::max(move+split,1e-30);
    return std::log(std::max(split/z,1e-4))-std::log(std::max(move/z,1e-4));
}
inline double keeper_split_prior(hb1::Row const& row){
    static hb1::Bound const bound{hb1::dirc_bind};
    auto x=bound.vec(row);double p[7];GBT_PROBA(kenma_queen,x.data(),p);
    return split_log_odds(p);
}
}
''')
p=dst/'policy.hpp';s=p.read_text();assert s.count('score = Params::split_value;')==1;s=s.replace('score = Params::split_value;','score = Params::split_value + kenma_split_log_odds;');assert s.count('score = Params::opening_production_value;')==1;s=s.replace('score = Params::opening_production_value;','score = Params::opening_production_value + kenma_split_log_odds;');s=s.replace('    hb1::Row const* hb_row = nullptr;','    double kenma_split_log_odds = 0.0;\n    hb1::Row const* hb_row = nullptr;');p.write_text(s)
p=dst/'main.cpp';s=p.read_text().replace('#include "kenma_pocket.hpp"','#include "kenma_pocket.hpp"\n#include "kenma_split_prior.hpp"').replace('            dec = pol.decide(w);','''            pol.kenma_split_log_odds = 0.0;
            if(w.me<=1 && w.len>=4 && pol.hb_row && !kenma::pocket_size(w))
                pol.kenma_split_log_odds = kenma::keeper_split_prior(*pol.hb_row);
            dec = pol.decide(w);''');p.write_text(s)
(dst/'README.md').write_text('''# Kenma22 — keeper split propensity inside search

Parent:08 (strategy equivalent to03), without21's reserve relay. Use the existing04 seven-class keeper model only for original queens of length>=4 outside proven sealed pockets. Sum four movement classes and three split classes; add log(P(split))−log(P(move)) at weight1 to ordinary split and opening-production split scores, with the existing1e-4 probability floor. Movement direction/path scores, split allocations, opening rescue, terminal escape and pocket rescue remain parent behavior. Nonqueens receive zero adjustment.

Motivation:04/05 hard action clones changed both movement and splitting;07/13 isolated movement advice and regressed. This tests the complementary split-timing information while preserving the stronger parent movement search. This model has only472 teacher split rows among26,820 queen turns; the prior is an unproven hypothesis, not a strong offline validation claim. No refit, game-result tuning or new data exposure.

Status: prepared for log-odds tests and recorded-observation integration checks. No game measurements or deployment checks yet. Reserved seeds11–13/new maps untouched. Model bytes copied exactly from04; original model provenance remains in04 README.
''')
print(dst)
