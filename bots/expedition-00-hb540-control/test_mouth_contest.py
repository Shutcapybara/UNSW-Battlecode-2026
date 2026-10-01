"""No-game topology, source, activation and switch-off checks for Expedition 10."""
import hashlib
import io
import json
import subprocess
import zipfile
import verify as v

NAME = 'expedition-10-mouthcontest'
BOT = v.BOTS / NAME


def main():
    manifest = json.loads((BOT / 'source-manifest.json').read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((BOT / name).read_bytes()).hexdigest() == digest, name
    assert (BOT / 'hb1_direction_compact.hpp').read_bytes() == (
        v.BOTS / v.BASE / 'hb1_direction_compact.hpp').read_bytes()
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in manifest:
            z.writestr(name, (BOT / name).read_bytes())
    assert len(archive.getvalue()) < 4 * 1024 * 1024
    code = r'''#include <cassert>
#include "mouth_contest.hpp"
int main() {
    ares::World w; w.W=7; w.H=5; w.NC=35;
    w.dest_tab.assign(140, ares::BLOCKED);
    assert(!ares::mouth_contested(w, 3)); // solitary foraging
    w.parts.push_back({0, 7, true, true, 1});
    w.ally_heads.push_back(0);
    assert(ares::mouth_contested(w, 0)); // occupied by ally
    assert(!ares::mouth_contested(w, 3)); // kelp, no route
    w.dest_tab[1]=3;
    assert(ares::mouth_contested(w, 3)); // one known step
    assert(!ares::mouth_contested(w, 4)); // not two steps
    w.dest_tab[3*4+1]=4;
    assert(!ares::mouth_contested(w, 4));
    w.dest_tab[1]=ares::UNKNOWN;
    assert(!ares::mouth_contested(w, 3));
    w.dest_tab[1]=ares::UNPAIRED;
    assert(!ares::mouth_contested(w, 3));
    assert(!ares::mouth_contested(w, -1));
    // Real portal topology: ally at (0,0) crosses E and lands remotely.
    w.ek.assign(70, ares::EK_KELP); w.epid.assign(70,-1);
    int first=w.ekey(0,1), second=w.ekey(24,3);
    w.ek[first]=w.ek[second]=ares::EK_PORTAL;
    w.epid[first]=w.epid[second]=17; w.pends[17]={first,second};
    w.rebuild_dest();
    assert(w.dest(0,1)==24);
    assert(ares::mouth_contested(w,24));
    assert(!ares::mouth_contested(w,1)); // geometric neighbor not landing
    // Toroidal seam uses actual known edge.
    w.ek[w.ekey(0,3)]=ares::EK_OPEN; w.rebuild_dest();
    assert(ares::mouth_contested(w,6));
    w.ally_heads.clear(); w.enemy_heads.push_back(0);
    assert(!ares::mouth_contested(w,24)); // enemies do not trigger ally cost
}
'''
    source = v.OUT / 'test-mouth-contest.cpp'
    source.write_text(code)
    exe = v.OUT / 'test-mouth-contest'
    subprocess.run(['clang++', '-std=c++20', '-O2', '-I', str(BOT), str(source), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
    samples = []
    fixtures = {}
    for rel in ['build/ra/golden/ares06-schooltime-A-1.jsonl',
                'build/cx/golden/portals-B-1/yuna-v03-core.jsonl.gz',
                'build/cx/golden/trauma-B-1/yuna-v03-core.jsonl.gz']:
        path = v.ROOT / rel
        fixtures[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        _, dragons = v.load(str(path))
        for _, d in sorted(dragons.items(), key=lambda x: (-len(x[1]['turns']), x[0]))[:2]:
            samples.append({'init': d['init'], 'turns': d['turns'][:250]})
    got = v.responses(v.compile_bot(BOT, NAME), samples)
    prior = v.responses(v.OUT / 'expedition-09-mouthroute', samples)
    parent = v.responses(v.OUT / v.BASE, samples)
    off = v.modified_copy(NAME, [('params.hpp', 'mouth_require_ally = true', 'mouth_require_ally = false')])
    assert v.responses(v.compile_bot(off, NAME + '-ungated'), samples) == prior
    off = v.modified_copy(NAME, [('params.hpp', 'mouth_enabled = true', 'mouth_enabled = false')])
    assert v.responses(v.compile_bot(off, NAME + '-off'), samples) == parent
    differences = sum(a != b for a, b in zip(got, prior))
    assert differences > 0, 'Gate has no observed activation in recorded sample'
    result = dict(turns=len(got), divergences_from_09=differences,
                  divergences_from_01=sum(a != b for a,b in zip(got,parent)),
                  switch_off_parity=True, topology_checks=True,
                  zip_bytes=len(archive.getvalue()), fixtures=fixtures,
                  game_performance='NOT TESTED')
    (v.OUT / 'mouth-contest-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
