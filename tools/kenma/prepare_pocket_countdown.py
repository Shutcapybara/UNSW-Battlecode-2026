"""Use observed pearl countdowns to retain a longer queen when local growth is safe."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
src=root/'bots/kenma-19-pocket-sprint';dst=root/'bots/kenma-20-pocket-countdown'
assert not dst.exists();shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
p=dst/'kenma_pocket.hpp';s=p.read_text();at=s.index('inline bool queen(')
s=s[:at]+'''// Only current legal observations are used: no atlas fertility or future RNG.
inline bool growth_pressure(ares::World const& w,std::vector<int> const& path) {
    std::vector<int> visited;int head=w.head;
    for(int d:path){head=w.dest(head,d);visited.push_back(head);}
    std::vector<int> cells{w.head};
    for(size_t i=0;i<cells.size();++i){
        int c=cells[i];
        if(w.seen[c]!=w.rnd+1)return true;
        if(w.pearl_seen[c]==w.rnd && std::find(visited.begin(),visited.end(),c)==visited.end())return true;
        if(w.bed[c]==1 && w.spawn_at[c]<=w.rnd+1)return true;
        for(int d=0;d<4;++d){int n=w.dest(c,d);if(n>=0 && std::find(cells.begin(),cells.end(),n)==cells.end())cells.push_back(n);}
        if(cells.size()>8)return true;
    }
    return false;
}
''' +s[at:]
a='''        // Keep two segments when possible, leaving slack for the next pearl.
        // Simulation charges sprint tax after each paid step and checks collision first.
        double score=-10.0*sim.body.size()-sim.eaten-0.1*path.size()
                     +(path.front()==w.face ? 0.01 : 0.0);'''
b='''        // Preserve a viable length-three queen unless observed food/countdowns
        // require slack. On the final turn, growth no longer needs an exit next turn.
        int length=static_cast<int>(sim.body.size());
        bool final_turn=w.rnd>=unswbc::Constants::MAX_ROUNDS-1;
        double score=(final_turn ? 10.0*length : -10.0*std::abs(length-3))
                     -(!final_turn && length>=3 && growth_pressure(w,path) ? 100.0 : 0.0)
                     -0.1*path.size()+(path.front()==w.face ? 0.01 : 0.0);'''
assert a in s;s=s.replace(a,b);p.write_text(s)
(dst/'README.md').write_text('''# Kenma20 — countdown-aware pocket length

Parent:19. Keep its local sprint option and full population cap. Prefer viable queen length3 after a candidate action when all pocket cells are freshly observed, all visible pearls have been consumed by that action, and no visible bed is due next round. Otherwise prefer length2. This uses World::spawn_at from the official observation countdown, never authored fertility or future random values. At the actual final round (MAX_ROUNDS−1), prefer maximum safe final length because no further exit is required. Existing exact movement simulation, sealed-component proof and split/donor rules remain unchanged.

Motivation:19 survives all8 Schooltime probes but ends at length2, which loses against a surviving length3 queen. All three15 failure streams explicitly show countdown1 on the turn with a safe preventive sprint. This refinement aims to preserve length3 between growth events. It is not assumed to solve all future uncertainty or guarantee survival.

Status: prepared; mechanism and actual game checks pending. No reserved seeds11–13/new maps used. Outputs belong under main build/kenma/.
''')
print(dst)
