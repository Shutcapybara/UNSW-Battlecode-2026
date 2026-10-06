from pathlib import Path
import shutil,json,sys
root=Path('/Users/alik/Documents/Projects/wt-kenma');sys.path.insert(0,str(root/'tools/kenma'))
from panel import fingerprint
peer=root.parent/'wt-bokuto/bots/bokuto-13-cull';parent=root/'bots/kenma-21-proven-reserve';dst=root/'bots/kenma-28-harvest-reserve'
assert fingerprint(peer)=='d192d721c4069fda8e42d3366b3a5161564f5548cfd06a67caf825941789d46b';assert not dst.exists()
shutil.copytree(peer,dst,ignore=shutil.ignore_patterns('.unswbc-build','*.zip'))
for name in ['kenma_pocket.hpp','kenma_reserve.hpp']:shutil.copyfile(parent/name,dst/name)
p=dst/'bokuto.hpp';s=p.read_text();a='    int depth_cap = 2;';assert s.count(a)==1;s=s.replace(a,'    bool reserve_needed = true; // Kenma28: only until an open queen component is proven.\n'+a)
a='if (!queen && w.units >= w.limit - 1)';assert s.count(a)==1;s=s.replace(a,'if (!queen && reserve_needed && w.units >= w.limit - 1)')
a='(queen || w.units < w.limit - 1)';assert s.count(a)==1;s=s.replace(a,'(queen || !reserve_needed || w.units < w.limit - 1)');p.write_text(s)
p=dst/'main.cpp';s=p.read_text().replace('#include "bokuto.hpp"','#include "bokuto.hpp"\n#include "kenma_pocket.hpp"\n#include "kenma_reserve.hpp"').replace('    bokuto::Guard guard;','    bokuto::Guard guard;\n    kenma::ReserveState reserve;')
a='            dec = pol.decide(w);';assert s.count(a)==1;s=s.replace(a,'''            if (kenma::donor(w)) {
                std::cout << "SPLIT 1\\nLOG kenma_pocket_donor\\nPROTOCOL 3\\nENDTURN\\n" << std::flush;
                continue;
            }
            const bool had_release = reserve.released;
            reserve.observe(w);
            if (reserve.released && !had_release) std::cout << "LOG kenma_reserve_released\\n";
            guard.reserve_needed = !reserve.released;
'''+a)
a='            pol.prepare_radio_for_decision(w, dec);';assert s.count(a)==1;s=s.replace(a,'            if (kenma::queen(w, pol, dec)) std::cout << "LOG kenma_pocket_queen\\n";\n'+a+'\n            reserve.tag(w, pol);');p.write_text(s)
(dst/'README.md').write_text('''# Kenma28 — Bokuto harvesting with proven reserve release and pocket protection

Copied from Bokuto13, runtime d192d721c4069fda8e42d3366b3a5161564f5548cfd06a67caf825941789d46b, whose reported Carthage screen is70–31–1. The source snapshot is copied into the Kenma namespace; Bokuto files remain unchanged. This preserves its guard, queen caution/hiding, sonar feeding, branch targets, spare-dragon culling and model.

Composition: copy Kenma21's proven small-pocket queen rescue, trapped donor culling and permanent open-component proof relay. The proof releases only the two global guard split reservations, preserving harvesting's local two-slot requirements. Original policy still sees the real unit limit. Pocket queen rescue runs after Bokuto's guard; packets are normalized before policy reading and flagged after preparation. No map identity, new model or parameter sweep.

Motivation:21 recovered the full four-map pool deficit by restricting the global reserve to queens that might need it. Bokuto13 adds a much stronger harvesting approach but retains that global reservation. This tests the composition; the peer's reported wins do not establish Kenma28's strength.

Status: prepared, unmeasured. Require combined sanitizer, fixed-observation parity and game/replay checks before any strength claim. No deployment or ladder request. Reserved seeds11–13/new maps untouched.
''')
report=dict(bot=dst.name,fingerprint=fingerprint(dst),bokuto_parent=fingerprint(peer),kenma_components_parent=fingerprint(parent))
(root.parent/'UNSW-Battlecode-2026/build/kenma/k28-source.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
