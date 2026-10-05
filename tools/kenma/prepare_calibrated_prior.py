"""Apply a development-distribution entropy match without changing model argmax."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
report=json.loads((MAIN/'build/kenma/stacked-prior/prior-scale.json').read_text())
assert report['row_metadata_exactly_equal'] and report['rows']==189630
assert round(report['entropy_matched_lambda'],2)==1.61
src=ROOT/'bots/kenma-17-stacked-direction-prior';dst=ROOT/'bots/kenma-18-entropy-matched-prior'
assert not dst.exists();shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
(dst/'kenma_prior.hpp').write_text(r'''// Sharpen and renormalize F/R/L probabilities before the unchanged search weight.
#pragma once
#include <algorithm>
#include <cmath>
namespace kenma {
inline void stacked_search_prior(int face,double const* p,double weight,double* absolute_logp) {
    static constexpr int rels[3]={0,1,3};
    double q[3],z=0;
    for(int i=0;i<3;++i){q[i]=std::pow(std::max(p[rels[i]],1e-30),1.61);z+=q[i];}
    for(int i=0;i<3;++i)absolute_logp[(face+rels[i])&3]=weight*std::log(std::max(q[i]/z,1e-4));
}
}
''')
p=dst/'policy.hpp';s=p.read_text().replace('#include "hb1_compact.hpp"','#include "hb1_compact.hpp"\n#include "kenma_prior.hpp"')
a='''            double z=kenma_stacked_p[0]+kenma_stacked_p[1]+kenma_stacked_p[3];
            for(int rel:{0,1,3}) {
                int d=(w.face+rel)&3;
                hb_logp[d]=Params::hb1_dir_lambda*std::log(std::max(kenma_stacked_p[rel]/std::max(z,1e-30),1e-4));
            }'''
assert s.count(a)==1;s=s.replace(a,'            kenma::stacked_search_prior(w.face,kenma_stacked_p,Params::hb1_dir_lambda,hb_logp);');p.write_text(s)
(dst/'README.md').write_text('''# Kenma18 — entropy-matched combined prior

Parent: kenma-17-stacked-direction-prior. Only changes how its four-class prediction becomes the movement search's F/R/L prior. Raise F/R/L probabilities to1.61 and renormalize, then apply the unchanged weight1.0 and1e-4 floor. Reverse stays at parent zero. Model, features, prediction argmax, search, splits, pocket rescue and reserved slot are unchanged. The parent HB fallback retains its original treatment.

Choice is from exactly aligned189,630 out-of-fold development predictions, not from a sweep over game results. Parent mean F/R/L entropy0.422933 versus A5-400 at0.562078; matching parent entropy requires exponent1.610885, rounded to1.61. Increasing the search weight alone also changes the absolute move-versus-split offset; renormalization preserves a probability prior and isolates confidence more cleanly. This is a distribution-scale hypothesis, not proof of a better game policy.

Status: prepared, unmeasured. Needs full Carthage comparison and exact-source deployment checks. Reserved seeds11–13/new maps untouched. Evidence main build/kenma/stacked-prior/prior-scale.json; generator tools/kenma/prepare_calibrated_prior.py.
''')
print(dst)
