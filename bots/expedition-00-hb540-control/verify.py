#!/usr/bin/env python3
"""CPU-only source, build, donor-feature and recorded-input checks; starts no games.
Run with .venv/bin/python bots/expedition-00-hb540-control/verify.py.
"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.cx.golden import Proc, canon, load

BOTS = ROOT / 'bots'
OUT = ROOT / 'build/expedition'
BASE = 'expedition-01-nodevil'
MANIFEST = json.loads(Path(__file__).with_name('manifest.json').read_text())


def compile_bot(source, name):
    exe = OUT / name
    subprocess.run(['clang++', '-std=c++20', '-O2', str(source / 'main.cpp'), '-o', str(exe)], check=True)
    return exe


def modified_copy(name, replacements):
    source = BOTS / name
    dest = OUT / 'switch-off' / name
    dest.mkdir(parents=True, exist_ok=True)
    for p in source.iterdir():
        if p.suffix in ('.cpp', '.hpp'):
            shutil.copy2(p, dest / p.name)
    for file, before, after in replacements:
        p = dest / file
        text = p.read_text()
        assert text.count(before) == 1, (name, before)
        p.write_text(text.replace(before, after))
    return dest


def responses(exe, samples):
    result = []
    for dragon in samples:
        proc = Proc([str(exe)], str(OUT))
        try:
            for i, turn in enumerate(dragon['turns']):
                reply = proc.ask((dragon['init'] if i == 0 else '') + turn['input'])
                assert reply is not None, f'No reply: {exe}'
                assert 'ares_fallback' not in reply, f'Fallback: {exe}'
                result.append(canon(reply, False, 'exact'))
        finally:
            proc.close()
    return result


def trap_activation_test():
    # Independent recorded inputs that bind the trap penalty on the frozen prior.
    # The broad original sample has zero trap-arm divergences; keep that fact and
    # this targeted activation check separate from closed-loop performance.
    path = ROOT / 'build/cx/golden/slithery_fight-A-1/yuna-v03-core.jsonl.gz'
    expected_sha = '486b93ae2be32f8f2c57631c53438ea4cc58d56620d28f2b9c724cb2a154ac9b'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha
    _, dragons = load(str(path))
    dragon = dragons[360]
    sample = [{'init': dragon['init'], 'turns': dragon['turns'][:500]}]
    parent = responses(OUT / BASE, sample)
    changed = responses(OUT / 'expedition-04-trap20', sample)
    assert len(parent) == len(changed) == 423
    different = [i for i, (a, b) in enumerate(zip(parent, changed)) if a != b]
    assert len(different) == 2 and different[0] == 166, different
    assert parent[166][0] == 'MOVE N' and changed[166][0] == 'MOVE W'
    assert dragon['turns'][166]['round'] == 243
    return dict(fixture=str(path.relative_to(ROOT)), sha256=expected_sha,
                dragon=360, turns=423, divergences=len(different), first_turn_index=166,
                first_round=243, parent_move='N', trap20_move='W', game_performance='NOT TESTED')


def donor_feature_test():
    outputs = []
    for label, header, typ, expression in [
        ('maelle', 'state.hpp', 'State', 'st.sat(st.box(st.ally, c), ares::Tun::s_ally)'),
        ('expedition', 'expedition_state.hpp', 'ExpeditionAllyState', 'st.feature(w, c)'),
    ]:
        include = BOTS / ('maelle-02-features' if label == 'maelle' else 'expedition-06-allycrowd')
        code = '''#include <cstdio>
#include "HEADER"
int main() {
    ares::World w; w.W=7; w.H=5; w.NC=35; w.head=17;
    w.pearl_seen.assign(w.NC,-1); w.seen.assign(w.NC,0);
    ares::TYPE st;
    for (int r : {0, 1, 2, 9, 25}) {
        w.rnd=r; w.parts.clear();
        w.parts.push_back({(r*3)%35,1,true,true,0});
        w.parts.push_back({(r*3+34)%35,1,true,false,0});
        w.parts.push_back({(r*7+1)%35,2,false,true,1});
        st.update(w);
        for(int c=0;c<35;c++) std::printf("%.17g\\n",EXPR);
    }
}
'''.replace('HEADER', header).replace('TYPE', typ).replace('EXPR', expression)
        source = OUT / f'feature-{label}.cpp'
        source.write_text(code)
        exe = OUT / f'feature-{label}'
        subprocess.run(['clang++', '-std=c++20', '-O2', '-I', str(include), str(source), '-o', str(exe)], check=True)
        outputs.append(subprocess.check_output([str(exe)]))
    assert outputs[0] == outputs[1], 'Ally feature differs from Maelle donor'
    return len(outputs[0].splitlines())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = {'source_checks': [], 'recorded_input_checks': [], 'game_benchmarks': 'NOT RUN'}
    for entry in MANIFEST:
        bot = BOTS / entry['bot']
        for filename, digest in entry['files'].items():
            assert hashlib.sha256((bot / filename).read_bytes()).hexdigest() == digest, (bot, filename)
        assert (bot / 'hb1_direction_compact.hpp').read_bytes() == (BOTS / 'hb1-14-prior-r540/hb1_direction_compact.hpp').read_bytes()
        z = io.BytesIO()
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as archive:
            for filename in entry['files']:
                archive.writestr(filename, (bot / filename).read_bytes())
        results['source_checks'].append({'bot': entry['bot'], 'runtime_zip_bytes': len(z.getvalue()), 'model_unchanged': True})
    for filename in MANIFEST[0]['files']:
        assert (BOTS / MANIFEST[0]['bot'] / filename).read_bytes() == (BOTS / 'hb1-14-prior-r540' / filename).read_bytes()
    results['ally_donor_values_equal'] = donor_feature_test()
    samples = []
    for rel in ['build/ra/golden/ares06-schooltime-A-1.jsonl',
                'build/cx/golden/portals-B-1/yuna-v03-core.jsonl.gz',
                'build/cx/golden/trauma-B-1/yuna-v03-core.jsonl.gz']:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f'Required recorded-input fixture: {path}')
        _, dragons = load(str(path))
        for _, d in sorted(dragons.items(), key=lambda x: (-len(x[1]['turns']), x[0]))[:2]:
            samples.append({'init': d['init'], 'turns': d['turns'][:250]})
    results['recorded_turns_per_bot'] = sum(len(d['turns']) for d in samples)
    # Native binaries were compiled in the first pass; rebuild if absent or stale.
    for entry in MANIFEST:
        name = entry['bot']; exe = OUT / name
        if not exe.exists() or any((BOTS / name / f).stat().st_mtime > exe.stat().st_mtime for f in entry['files']):
            compile_bot(BOTS / name, name)
    baseline = responses(OUT / BASE, samples)
    control = responses(OUT / MANIFEST[0]['bot'], samples)
    for entry in MANIFEST[2:]:
        name = entry['bot']; got = responses(OUT / name, samples)
        n = sum(a != b for a, b in zip(baseline, got))
        results['recorded_input_checks'].append({'bot': name, 'enabled_divergences': n})
        print(name, 'enabled divergences:', n, flush=True)
    results['trap_activation'] = trap_activation_test()
    print('Trap penalty: targeted recorded-input activation confirmed', flush=True)
    # Parameter-only arms restore byte-identical source to their parent.
    for name, key, changed, original in [
        ('expedition-02-threat05','threat_weight','0.5','1.0'),
        ('expedition-03-revisit005','visit_weight','0.05','0.15'),
        ('expedition-04-trap20','trap_weight','20.0','30.0'),
        ('expedition-05-explore3','unseen_value','3.0','5.0')]:
        for f in MANIFEST[1]['files']:
            value = (BOTS / name / f).read_text()
            if f == 'params.hpp': value = value.replace(f'double {key} = {changed};', f'double {key} = {original};')
            assert value == (BOTS / BASE / f).read_text(), (name, f)
    off = [
        (BASE, [('params.hpp', 'expedition_identity_terms = false', 'expedition_identity_terms = true')], control),
        ('expedition-06-allycrowd', [('params.hpp', 'expedition_ally_weight = -1.4', 'expedition_ally_weight = 0.0')], baseline),
        ('expedition-07b-sparse48-384', [('policy.hpp', 'if (age >= 2)\n            cap = Params::expedition_cap_lo', 'if (false)\n            cap = Params::expedition_cap_lo')], baseline),
        ('expedition-08-symmetry', [('params.hpp', 'sym_infer = true', 'sym_infer = false')], baseline),
        ('expedition-09-mouthroute', [('params.hpp', 'mouth_enabled = true', 'mouth_enabled = false')], baseline),
    ]
    for name, replacements, expected in off:
        source = modified_copy(name, replacements)
        exe = compile_bot(source, name + '-off')
        got = responses(exe, samples)
        divergences = sum(a != b for a, b in zip(expected, got))
        results.setdefault('switch_off', []).append({'bot': name, 'divergences': divergences})
        assert got == expected, (name, divergences)
        print(name, 'switch-off parity: 0 divergent', flush=True)
    (OUT / 'verification.json').write_text(json.dumps(results, indent=2) + '\n')
    print('PASS:', results['recorded_turns_per_bot'], 'recorded turns per arm; no games started', flush=True)


if __name__ == '__main__':
    main()
