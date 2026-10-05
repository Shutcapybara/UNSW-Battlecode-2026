"""One predeclared queen-only geometric blend; no training or shared-file mutation."""
from pathlib import Path
import json,shutil,zipfile
root=Path(__file__).resolve().parents[2];out=root.parent/'UNSW-Battlecode-2026/build/kenma/teacher213'
report=json.loads((out/'report.json').read_text());assert report['argmax_equal']==report['parity_rows']==2832 and report['max_probability_error']<1e-6
p=root/'bots/kenma-27-queen213-blend';assert not p.exists();shutil.copytree(root/'bots/kenma-21-proven-reserve',p,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
for f in ['hb1_compact.hpp','hb1_direction_compact.hpp']:shutil.copy2(root/'bots/kenma-16-lossless-model-text'/f,p/f)
for src,dst in [('teacher213.hpp','kenma_teacher213_model.hpp'),('gbt_compact.hpp','gbt_compact.hpp')]:shutil.copy2(out/src,p/dst)
(p/'kenma_blend.hpp').write_text('''#pragma once
#include <array>
#include <vector>
#include <cmath>
#include <algorithm>
namespace kenma {
inline std::vector<double> blend_direction(std::vector<double> const& parent,std::array<double,3> const& teacher){
 std::vector<double> p(3);double z=0;
 for(int i=0;i<3;++i){p[i]=std::sqrt(std::max(parent[i],1e-4)*std::max(teacher[i],1e-4));z+=p[i];}
 for(auto& v:p)v/=z;return p;
}
}
''')
(p/'kenma_teacher213.hpp').write_text('''#pragma once
#include <array>
#include <cmath>
#include <stdexcept>
#include "hb1_compact.hpp"
#include "gbt_compact.hpp"
#include "kenma_teacher213_model.hpp"
namespace kenma {
inline std::array<double,3> teacher_direction(hb1::Row const& row){
 static_assert(teacher213::K==4 && teacher213::N_FEAT==270);
 static hb1::Bound const bound{hb1::dirc_bind};auto x=bound.vec(row);double p[4];
 GBT_PROBA(teacher213,x.data(),p);double z=p[0]+p[1]+p[3];
 if(!std::isfinite(z)||z<=0)throw std::runtime_error("teacher probability");
 return {p[0]/z,p[1]/z,p[3]/z};
}
}
''')
f=p/'policy.hpp';s=f.read_text().replace('#include "world.hpp"','#include "world.hpp"\n#include "kenma_blend.hpp"');s=s.replace('    hb1::Row const* hb_row = nullptr;','    bool kenma_teacher_active=false;\n    std::array<double,3> kenma_teacher_probs{};\n    hb1::Row const* hb_row = nullptr;');needle='            auto p = hb1::dirc_proba(dir_bound.vec(*hb_row));';assert s.count(needle)==1;s=s.replace(needle,needle+'\n            if(kenma_teacher_active && w.me<=1)\n                p=kenma::blend_direction(p,{kenma_teacher_probs[hb1::dirc_classes[0]],kenma_teacher_probs[hb1::dirc_classes[1]],kenma_teacher_probs[hb1::dirc_classes[2]]});');f.write_text(s)
f=p/'main.cpp';s=f.read_text().replace('#include "kenma_reserve.hpp"','#include "kenma_reserve.hpp"\n#include "kenma_teacher213.hpp"');needle='            dec = pol.decide(w);';assert s.count(needle)==1;s=s.replace(needle,'''            pol.kenma_teacher_active=false;
            if(w.me<=1 && !kenma::pocket_size(w)) {
                try {
                    if(!pol.hb_row)throw std::runtime_error("missing HB row");
                    pol.kenma_teacher_probs=kenma::teacher_direction(*pol.hb_row);
                    pol.kenma_teacher_active=true;
                    std::cout<<"LOG kenma_teacher_active\\n";
                } catch(...) {std::cout<<"LOG kenma_teacher_fallback\\n";}
            }
'''+needle);f.write_text(s)
(p/'README.md').write_text(f'''# Kenma27 — coherent teacher direction blended only for open-map queens

Parent21 (Carthage60–42), with16's previously verified lossless parent-model storage. Only original queens outside a proven sealed pocket receive a direction-prior change. Their F/R/L prior is the normalized geometric mean of the parent and team213 distributions, weight0.5 each, with the existing1e-4 floor applied before blending. Nonqueen prior, move search, splitting, pocket rescue and reserve relay remain21. Model class order F/R/B/L; back is removed and F/R/L renormalized. No fit or weight sweep.

Existing source: Hinata A1-team213 full400-round refit, SHA256 {report['source_sha256']}.270 HB features in verified parent-binding order;1600trees,196404nodes. Lane-local export corrects LightGBM missing_type=None NaN routing to the zero comparison; the shared exporter and measured ancestors are unchanged. Native probabilities match LightGBM on2832 real/missing-value samples (max error {report['max_probability_error']:.3g}, all argmax equal). This is implementation evidence only, not strength evidence.

Motivation: pooled drop-in priors regressed. A coherent teacher is new evidence; restricting its blend to queens preserves the direction prior that carries most of the team's economy. This remains speculative: teacher213's full-move model was not fitted solely to queens, and the parent still controls split timing.

Status: prepared, unmeasured. Exact combined archive, runtime integration, activation/fallback audit and sandbox compute remain required before deployment; no game queue. Reserved seeds11–13/new maps untouched.
''')
with zipfile.ZipFile(out/'kenma-27-provisional.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(p.iterdir()):
  if f.is_file():z.write(f,f.name)
size=(out/'kenma-27-provisional.zip').stat().st_size;assert size<4*1024**2;print(json.dumps(dict(bot=p.name,zip_bytes=size,headroom=4*1024**2-size)),flush=True)
