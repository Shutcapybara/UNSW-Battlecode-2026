"""Create an immutable standalone C++ model artifact under build/, without modifying its chassis.

Large generated actor headers belong in the local artifact, not tracked bot snapshots.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import torch
from model import Scorer, export_header

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.finals.screen import source_hash


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--action', type=Path)
    ap.add_argument('--sonar', type=Path)
    ap.add_argument('--suppress-optional', action='store_true', help='Control arm: keep only beacon/handoff packet families')
    ap.add_argument('--chassis', default='bokuto-65-policy-collector', choices=['bokuto-65-policy-collector', 'bokuto-68-sonar-history'])
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.sonar and args.suppress_optional:
        ap.error('Suppression control cannot also use a learned sonar actor')
    output = args.output.resolve()
    if output.exists():
        ap.error('Output exists; export a new immutable version')
    if not output.is_relative_to(ROOT / 'build') and not output.is_relative_to(Path('/tmp')):
        ap.error('Generated model artifacts must stay under build/ or /tmp')
    parent = ROOT / 'bots' / args.chassis
    shutil.copytree(parent, output, ignore=shutil.ignore_patterns('.unswbc-build', 'build', '__pycache__'))
    manifest = dict(parent=args.chassis, parent_sha256=source_hash(parent), actors={},
                    fixed_chassis_prior='Inherited frozen HB1 direction GBT, hb1_dir_lambda=1.0; training critic is not exported')
    main = (output / 'main.cpp').read_text()
    for actor in ('action', 'sonar'):
        checkpoint = getattr(args, actor)
        if checkpoint is None:
            manifest['actors'][actor] = 'fixed-incumbent'
            continue
        state = torch.load(checkpoint, map_location='cpu', weights_only=True)
        if state['actor'] != actor:
            ap.error('Checkpoint actor mismatch')
        model = Scorer(); model.load_state_dict(state['state'])
        export_header(model, output / f'{actor}_model.hpp', actor)
        archive = output.parent / (output.name + f'.{actor}.pt')
        shutil.copyfile(checkpoint, archive)
        main = main.replace('#include "options.hpp"', f'#include "options.hpp"\n#include "{actor}_model.hpp"', 1)
        manifest['actors'][actor] = dict(checkpoint=str(archive.resolve()), original_checkpoint=str(checkpoint.resolve()),
            checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(), iteration=state.get('iteration', 'clone'))
    if args.action:
        main = main.replace('            int selected = 0;', '''            int selected = 0;
            if (!FINALS_RPC && turn.candidates.size() > 1) {
                auto context = finals::exported::action_encode(observation);
                float best = -std::numeric_limits<float>::infinity();
                for (size_t i = 0; i < turn.candidates.size(); i++) {
                    float score = finals::exported::action_score(context, turn.candidates[i].features);
                    if (turn.candidates[i].available && score > best) { best = score; selected = i; }
                }
            }''', 1)
    if args.sonar:
        feature_call = 'finals::packet_features(w, pol, dec, packets[ray][i]' + (
            ', previous_sends)' if args.chassis == 'bokuto-68-sonar-history' else ')')
        main = main.replace('            std::array<int, 4> sends{0, 0, 0, 0};', '''            std::array<int, 4> sends{0, 0, 0, 0};
            if (!FINALS_RPC) {
                auto context = finals::exported::sonar_encode(observation);
                for (int ray = 0; ray < 4; ray++) {
                    float best = -std::numeric_limits<float>::infinity();
                    for (size_t i = 0; i < packets[ray].size(); i++) {
                        auto features = FEATURE_CALL;
                        float score = finals::exported::sonar_score(context, features);
                        if (score > best) { best = score; sends[ray] = i; }
                    }
                }
            }'''.replace('FEATURE_CALL', feature_call), 1)
    # Rare guard changes must retain actual-command diagnostics even in deployment.
    main = main.replace('if (FINALS_RPC || FINALS_TRACE) {',
                        'if (FINALS_RPC || FINALS_TRACE || turn.unexpected_override) {', 1)
    if args.suppress_optional:
        main = main.replace('            finals::commit_packets(pol, packets, sends);', '''            finals::commit_packets(pol, packets, sends);
            if (!FINALS_RPC) {
                for (int ray = 0; ray < 4; ray++) {
                    int type = 0; uint64_t bits = 0;
                    if (pol.sonar_out[ray] && ares::Policy::unpack(w, pol.sonar_out[ray], type, bits) &&
                        type != 1 && type != 3 && type != 7) pol.sonar_out[ray] = 0;
                }
                pol.sonar_order.erase(std::remove_if(pol.sonar_order.begin(), pol.sonar_order.end(),
                    [&](int ray) { return !pol.sonar_out[ray]; }), pol.sonar_order.end());
            }''', 1)
    manifest['optional_packet_suppression'] = args.suppress_optional
    (output / 'main.cpp').write_text(main)
    # Remove unused historical atlas data physically, while retaining the empty interface.
    (output / 'atlas.hpp').write_text('''#pragma once
namespace ares::atlas {
struct Map { int W,H; const char* name; const char* edges; const int* portals; int n_portals; const char* beds; };
inline constexpr int n_maps=0;
inline constexpr Map maps[1]={{0,0,nullptr,nullptr,nullptr,0,nullptr}};
}
''')
    (output / 'README.md').write_text(f'# {output.name}\n\nGenerated standalone C++ actor artifact from Bokuto 65.\n'
                                    'No RPC/trace at default compilation. No stored atlas.\n'
                                    'No strength or promotion claim; see export-manifest.json.\n')
    manifest['artifact_sha256'] = source_hash(output)
    manifest['exporter_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / 'export-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    executable = output.parent / (output.name + '.native')
    subprocess.run(['g++', '-std=c++20', '-O2', str(output / 'main.cpp'), '-o', str(executable)], check=True, timeout=120)
    print(json.dumps(dict(artifact=str(output), executable=str(executable), manifest=manifest), indent=2))


if __name__ == '__main__':
    main()
