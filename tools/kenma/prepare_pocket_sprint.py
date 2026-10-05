"""Local length control inside proven sealed pockets; no global population reserve."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
src=root/'bots/kenma-15-pocket-without-reserve';dst=root/'bots/kenma-19-pocket-sprint'
assert not dst.exists();shutil.copytree(src,dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__'))
p=dst/'kenma_pocket.hpp';s=p.read_text();a=s.index('    double best=-1e30;');b=s.index('    return true;',a)
s=s[:a]+'''    double best=-1e30;
    std::vector<int> best_path;
    auto consider=[&](std::vector<int> const& path) {
        auto sim=pol.simulate(w,path);
        if (sim.status!=ares::Policy::SimStatus::OK) return;
        // Keep two segments when possible, leaving slack for the next pearl.
        // Simulation charges sprint tax after each paid step and checks collision first.
        double score=-10.0*sim.body.size()-sim.eaten-0.1*path.size()
                     +(path.front()==w.face ? 0.01 : 0.0);
        if (score>best) { best=score; best_path=path; }
    };
    for (int d=0; d<4; ++d) {
        consider({d});
        if(w.len==2 || w.len==3)for(int e=0;e<4;++e)consider({d,e});
    }
    if (best_path.empty()) return false;
    out.act=ares::Act::MOVE; out.dirs=best_path; out.why='q'; out.target=w.head;
''' +s[b:];p.write_text(s)
p=dst/'main.cpp';s=p.read_text().replace('            kenma::queen(w,pol,dec);','            if(kenma::queen(w,pol,dec) && dec.act==ares::Act::MOVE && dec.dirs.size()==2)\n                std::cout << "LOG kenma_pocket_sprint\\n";');p.write_text(s)
(dst/'README.md').write_text('''# Kenma19 — pocket sprint length control

Parent: kenma-15-pocket-without-reserve. Preserve its full population limit outside a proven sealed pocket. The original queen now compares legal one-step and, at length2/3, two-step moves inside that pocket. Prefer shorter final body, then fewer pearls, then shorter action; preserve the facing tie-break. Exact parent simulation checks collisions and charges paid-step length. Existing length>=4 split and trapped-donor culling remain unchanged. No orbit, learned model change, map identity or new terrain exposure.

Mechanism:15 died in three Schooltime probes when a pearl grew its length3 queen to4 while the team reached its population cap. All three recorded streams had legal two-step length3→2 paths before the fatal growth. Keeping slack locally could avoid the global reserve that caused four UNSW pool losses. This is a hypothesis until tested in actual games; future food and population are not assumed known.

Status: prepared for sanitizer mechanism checks, then Schooltime seeds1/2/3/5 both seats and eight UNSW seed1 pool probes. No promotion claim; reserved seeds11–13/new maps untouched.
''')
print(dst)
