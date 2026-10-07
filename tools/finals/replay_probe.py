"""Reconstruct legal local-replay histories and audit a bot's decisions offline.

Compile a diagnostic copy under --output, never edit the measured snapshot.
Probe movement versus production/escape ordering and the final guard decision.
Reconstruction is restricted to local unredacted replays; server countdowns need oracle.py.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/learn'))
import rebuild
from tools.analysis.features.frame import decode


PROBE_CPP = r'''
inline void finals_probe(const ares::World& w, const ares::Policy& p,
                         const ares::Decision& before, const ares::Decision& after,
                         char guard_tag) {
    int crowd = 0;
    for (int pi : w.ally_heads)
        if (after.target >= 0 && w.tdist(w.parts[pi].cell, after.target) <= 3) crowd++;
    std::string command = after.act == ares::Act::SPLIT ? "SPLIT " + std::to_string(after.split) : "MOVE ";
    if (after.act == ares::Act::MOVE) for (int d : after.dirs) command += ares::dir_char(d);
    fprintf(stderr, "FD {\"id\":%d,\"round\":%d,\"length\":%d,\"body_size\":%zu,"
        "\"head\":%d,\"tail\":%d,\"units\":%d,\"limit\":%d,\"target\":%d,\"crowd\":%d,"
        "\"escape_size\":%d,\"before_why\":\"%c\",\"why\":\"%c\",\"guard\":\"%c\","
        "\"command\":\"%s\"}\n", w.me,w.rnd,w.len,w.body.size(),w.head,
        w.body.empty() ? -1 : w.body.front(),w.units,w.limit,after.target,crowd,
        p.tyr_escape_split(w),before.why,after.why,guard_tag ? guard_tag : '-',command.c_str());
}
'''

ORDER_CPP = r'''
        fprintf(stderr, "FO {\"id\":%d,\"round\":%d,\"move_score\":%.9g,"
            "\"after_production_score\":%.9g,\"escape_size\":%d,\"production\":%s}\n",
            w.me,w.rnd,finals_move_score,best_score,tyr_escape_split(w),
            selected.act == Act::SPLIT ? "true" : "false");
'''


def compile_probe(source, out):
    copied = out / 'source'
    shutil.copytree(source, copied, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('.unswbc-build', 'build', '__pycache__'))
    main = (copied / 'main.cpp').read_text()
    main = main.replace('int main() {', PROBE_CPP + '\nint main() {', 1)
    main = main.replace('dec = pol.decide(w);', 'dec = pol.decide(w);\n            const auto finals_before = dec;', 1)
    main = main.replace('pol.prepare_radio_for_decision(w, dec);',
                        'finals_probe(w, pol, finals_before, dec, guard_tag);\n'
                        '            pol.prepare_radio_for_decision(w, dec);', 1)
    (copied / 'main.cpp').write_text(main)
    policy = (copied / 'policy.hpp').read_text()
    policy = policy.replace('double split_score = 0.0;',
                            'const double finals_move_score = best_score;\n        double split_score = 0.0;', 1)
    policy = policy.replace('if (best_score < -900.0) {', ORDER_CPP + '\n        if (best_score < -900.0) {', 1)
    (copied / 'policy.hpp').write_text(policy)
    exe = out / 'probe'
    # The current official helper uses C++20 defaulted equality and contains().
    subprocess.run(['g++', '-std=c++20', '-O2', str(copied / 'main.cpp'), '-o', str(exe)],
                   check=True, timeout=120)
    return exe


def probe(replay, source, seat, output, max_dragons, causes):
    output.mkdir(parents=True, exist_ok=True)
    frame = decode(replay)
    targets = sorted({e['id'] for e in frame['events']['deaths']
                      if e['team'] == seat and e['cause'] in causes and e['id'] > 1})[:max_dragons]
    if not targets:
        raise ValueError('No matching worker deaths')
    trajectories = defaultdict(list)
    spawns = {}

    def emit(dragon, spawn, block, ctx):
        if dragon in targets:
            spawns[dragon] = spawn
            trajectories[dragon].append((block, ctx))

    rebuild.walk(replay.read_bytes(), emit)
    exe = compile_probe(source, output)
    records, mismatches = [], []
    turns = 0
    for dragon in targets:
        spawn = spawns[dragon]
        prefix = (f"ID {dragon}\nTEAM {spawn['team']}\nMAP {spawn['W']} {spawn['H']}\n"
                  f"UNIT_LIMIT {spawn['unit_limit']}\n")
        sequence = trajectories[dragon]
        text = prefix + ''.join(block for block, ctx in sequence) + 'ENDGAME\n'
        (output / f'dragon-{dragon}.input').write_text(text)
        run = subprocess.run([str(exe)], input=text, capture_output=True, text=True, timeout=60)
        if run.returncode:
            raise RuntimeError(f'Probe dragon {dragon} exited {run.returncode}: {run.stderr[-500:]}')
        (output / f'dragon-{dragon}.stdout').write_text(run.stdout)
        (output / f'dragon-{dragon}.stderr').write_text(run.stderr)
        replies = [part.strip() for part in run.stdout.split('ENDTURN') if part.strip()]
        if len(replies) != len(sequence):
            raise ValueError(f'Dragon {dragon}: {len(replies)} replies for {len(sequence)} blocks')
        orders = {}
        for line in run.stderr.splitlines():
            if line.startswith('FO '):
                r = json.loads(line[3:])
                orders[r['round']] = r
        for line in run.stderr.splitlines():
            if line.startswith('FD '):
                r = json.loads(line[3:])
                r.update(orders.get(r['round'], {}))
                records.append(r)
        for reply, (_, ctx) in zip(replies, sequence):
            turns += 1
            commands = [line for line in reply.splitlines() if line.startswith(('MOVE ', 'SPLIT '))]
            action = ctx['action']
            expected = None if action is None else f'{action[0].upper()} {action[1]}'
            if commands != [expected]:
                mismatches.append(dict(id=dragon, round=ctx['round'], expected=expected, commands=commands))
    masked = [r for r in records if r.get('move_score', 0) < -900 and
              r.get('after_production_score', -1000) >= -900 and r.get('escape_size', 0) > 0]
    deaths = [e for e in frame['events']['deaths'] if e['id'] in targets]
    result = dict(replay=str(replay), replay_sha256=hashlib.sha256(replay.read_bytes()).hexdigest(),
                  source=str(source), seat=seat, dragons=targets, turns=turns,
                  action_mismatches=mismatches, production_masks_escape=masked,
                  deaths=deaths, last_decisions=[r for r in records if any(
                      r['id'] == e['id'] and 0 <= e['round'] - r['round'] <= 2 for e in deaths)])
    (output / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
    (output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in result.items()}, indent=2))
    return 1 if mismatches else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT / 'bots/bokuto-18-queenfeed')
    parser.add_argument('--seat', choices=['A', 'B'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-dragons', type=int, default=12)
    parser.add_argument('--causes', nargs='+', default=['wall', 'self'])
    args = parser.parse_args()
    return probe(args.replay.resolve(), args.source.resolve(), args.seat,
                 args.output.resolve(), args.max_dragons, args.causes)


if __name__ == '__main__':
    sys.exit(main())
