"""Trajectory block parity: Python traj.py against C++ cpp/learn_traj.hpp on the exact blocks each process received
in replays (rebuild.walk), plus invariants. Run where g++ exists:
    python tools/learn/test_traj_parity.py REPLAY [...]"""
import os, subprocess, sys, tempfile, collections
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rebuild, block as B, traj as T


def main(paths):
    lines = []; n = 0; stats = collections.Counter()
    for p in paths:
        turns = collections.defaultdict(list)
        rebuild.walk(Path(p).read_bytes(), lambda i, sp, txt, ctx: turns[i].append((sp, txt)))
        for did, seq in turns.items():
            sp = seq[0][0]
            spawn_txt = f"ID {sp['id']}\nTEAM {sp['team']}\nMAP {sp['W']} {sp['H']}\nUNIT_LIMIT {sp['unit_limit']}\n"
            t = T.Traj(B.parse_spawn(spawn_txt))
            lines += ['SPAWN', spawn_txt.rstrip('\n'), 'END']
            prev_r = None
            for _, txt in seq:
                b = B.parse_block(txt)
                v = t.observe(b)
                assert len(v) == T.N_T and all(isinstance(x, int) for x in v)
                assert 1 <= v[6] <= 20 and 0 <= v[4] <= v[6] and 0 <= v[5] <= v[4]
                assert prev_r is None or b.round > prev_r
                prev_r = b.round
                stats['units_d20_known'] += v[0] != T.BIG; stats['enemy_seen'] += v[3] >= 0; stats['contact_now'] += v[3] == 0
                lines += ['BLOCK', txt.rstrip('\n'), 'END', 'T ' + ' '.join(map(str, v))]
                n += 1
    here = Path(__file__).parent / 'cpp'
    with tempfile.TemporaryDirectory() as d:
        exe = f'{d}/tp'
        subprocess.run(['g++', '-std=c++20', '-O2', f'-I{here}', str(here / 'traj_parity_main.cpp'), '-o', exe], check=True)
        r = subprocess.run([exe], input='\n'.join(lines) + '\n', capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr.strip()[:300])
    print('python turns', n, dict(stats))
    return r.returncode


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
