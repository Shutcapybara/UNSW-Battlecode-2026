"""No-game activation and safety-boundary checks for the frozen food-hold arm."""
import hashlib
import io
import json
import subprocess
import zipfile
import verify as v

NAME = 'expedition-11-foodhold'
BOT = v.BOTS / NAME


def main():
    manifest = json.loads((BOT / 'source-manifest.json').read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((BOT / name).read_bytes()).hexdigest() == digest
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in manifest:
            z.writestr(name, (BOT / name).read_bytes())
    assert len(archive.getvalue()) < 4 * 1024 * 1024
    source = v.OUT / 'test-food-hold.cpp'
    source.write_text(r'''#include <cassert>
#include "food_hold.hpp"
int main() {
    using ares::hold_split_for_food;
    assert(hold_split_for_food(149,true,true,1,1,-1,12,12));
    assert(!hold_split_for_food(150,true,true,1,1,-1,12,12));
    assert(!hold_split_for_food(1,false,true,1,1,-1,12,12));
    assert(!hold_split_for_food(1,true,false,1,1,-1,12,12));
    assert(!hold_split_for_food(1,true,true,2,1,-1,12,12));
    assert(!hold_split_for_food(1,true,true,1,0,-1,12,12));
    assert(!hold_split_for_food(1,true,true,1,1,0,12,12));
    assert(!hold_split_for_food(1,true,true,1,1,-1,11,12));
}
''')
    exe = v.OUT / 'test-food-hold'
    subprocess.run(['clang++','-std=c++20','-O2','-I',str(BOT),str(source),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
    samples = []; fixtures = {}
    for rel in ['build/ra/golden/ares06-schooltime-A-1.jsonl',
                'build/cx/golden/portals-B-1/yuna-v03-core.jsonl.gz',
                'build/cx/golden/trauma-B-1/yuna-v03-core.jsonl.gz']:
        path = v.ROOT / rel
        fixtures[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        _, dragons = v.load(str(path))
        for _, d in sorted(dragons.items(), key=lambda x: (-len(x[1]['turns']), x[0]))[:2]:
            samples.append({'init':d['init'], 'turns':d['turns'][:250]})
    parent = v.responses(v.OUT / v.BASE, samples)
    got = v.responses(v.compile_bot(BOT, NAME), samples)
    off = v.modified_copy(NAME, [('params.hpp','food_hold_enabled = true','food_hold_enabled = false')])
    assert v.responses(v.compile_bot(off, NAME+'-off'), samples) == parent
    changes = [(i,a[0],b[0]) for i,(a,b) in enumerate(zip(parent,got)) if a != b]
    assert changes, 'No recorded activation; investigate before games'
    result = dict(turns=len(got), divergences=len(changes), first_changes=changes[:12],
                  switch_off_parity=True, boundary_checks=True, zip_bytes=len(archive.getvalue()),
                  fixtures=fixtures, game_performance='NOT TESTED')
    (v.OUT/'food-hold-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
