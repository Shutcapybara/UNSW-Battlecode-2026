"""Release the global reserve only after a shared terrain proof about the queen."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
src=root/'bots/kenma-08-lossless-direction';dst=root/'bots/kenma-21-proven-reserve'
assert not dst.exists();shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
(dst/'kenma_reserve.hpp').write_text(r'''#pragma once
#include "kenma_pocket.hpp"
namespace kenma {
// Terrain is fixed. Nine open-connected cells or an incident portal prove that
// the queen cannot inhabit a closed <=8-cell, portal-free component now or later.
inline bool queen_component_open(ares::World const& w,int start) {
    std::vector<int> cells{start};
    for(size_t i=0;i<cells.size();++i)for(int d=0;d<4;++d){
        auto kind=w.ek[w.ekey(cells[i],d)];
        if(kind==ares::EK_PORTAL)return true;
        if(kind!=ares::EK_OPEN)continue;
        int n=w.nbr(cells[i],d);
        if(std::find(cells.begin(),cells.end(),n)==cells.end()){
            cells.push_back(n);if(cells.size()>8)return true;
        }
    }
    return false;
}
struct ReserveState {
    bool released=false;
    void observe(ares::World& w){
        // High type bit is an envelope flag. Preserve all 44 payload bits,
        // including the high density-report id bit, and repair the checksum.
        for(auto& msg:w.msgs){int type=0;uint64_t payload=0;
            if(!ares::Policy::unpack(w,msg,type,payload))continue;
            if((type&8) && (type&7)){
                released=true;msg=ares::Policy::pack(w,type&7,payload);
            }
        }
        if(released)return;
        if(w.me<=1 && queen_component_open(w,w.head))released=true;
        for(int pi:w.ally_heads){auto const& q=w.parts[pi];
            if(q.id<=1 && queen_component_open(w,q.cell))released=true;
        }
    }
    void tag(ares::World const& w,ares::Policy& pol)const{
        if(!released)return;
        for(auto& msg:pol.sonar_out){if(!msg)continue;int type=0;uint64_t payload=0;
            if(ares::Policy::unpack(w,msg,type,payload) && type>=1 && type<=7)
                msg=ares::Policy::pack(w,type|8,payload);
        }
    }
};
}
''')
p=dst/'main.cpp';s=p.read_text().replace('#include "kenma_pocket.hpp"','#include "kenma_pocket.hpp"\n#include "kenma_reserve.hpp"').replace('    ares::Policy pol;','    ares::Policy pol;\n    kenma::ReserveState reserve;').replace('            const int real_limit=w.limit;','            const bool had_release=reserve.released;\n            reserve.observe(w);\n            if(reserve.released && !had_release)std::cout << "LOG kenma_reserve_released\\n";\n            const int real_limit=w.limit;').replace('if (w.me>1) w.limit=std::max(1,real_limit-1);','if (w.me>1 && !reserve.released) w.limit=std::max(1,real_limit-1);').replace('            pol.prepare_radio_for_decision(w, dec);','            pol.prepare_radio_for_decision(w, dec);\n            reserve.tag(w,pol);');p.write_text(s)
(dst/'README.md').write_text('''# Kenma21 — release only a proven unnecessary reserve

Parent:08 (strategy equivalent to03). Preserve the original queen keeper and donor behavior. A process releases its one-slot population reserve only after proving that its original queen belongs to an open-connected component of at least9 cells, or one containing a portal. Static terrain means such a queen can never enter a distinct closed <=8-cell, portal-free component where this keeper requires a reserve. Unknown edges are ignored, not treated as open. A nonqueen can seed the proof only from an observed allied original queen, never from its own large component.

Share the permanent fact using the unused high type bit of existing policy sonar packets. Recompute the checksum; receivers remove the envelope flag before parent decoding. All44 payload bits (including the high density id bit), packet order, ray count, split handoff and HB message-count features are preserved. No new rays, map identity or full-map inference. As with parent radio, team tag/checksum is not cryptographic authentication.

Motivation:15 removed four UNSW pool losses caused by the global reserve, but killed3/8 Schooltime queens;19/20 survived all8 but ended at length2.21 keeps03's length3 pocket keeper while removing reserve cost only where the terrain proof makes that reserve unnecessary.

Status: prepared for terrain/message-preservation tests and bounded Schooltime/UNSW probes. No reserved seeds11–13/new maps used. Source and results remain in the Kenma lane.
''')
print(dst)
