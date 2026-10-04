"""The in-bot path (official helper.hpp -> learn_helper.hpp -> encoder) equals the Python encoder, per process.
    python3 tools/learn/test_helper_parity.py HELPER_DIR fixture.txt   (fixture from test_parity.py)"""
import sys, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).parent
helper_dir, fx = sys.argv[1], sys.argv[2]
exe = Path(tempfile.gettempdir()) / 'learn_helper_parity'
subprocess.run(['g++', '-std=c++20', '-O2', f'-I{helper_dir}', '-o', str(exe), str(HERE / 'cpp' / 'helper_parity_main.cpp')], check=True)
procs, cur = [], None
lines = Path(fx).read_text().split('\n')
i = 0
while i < len(lines):
    l = lines[i]
    if l == 'PROC':
        cur = dict(spawn='', blocks=[], ex=[]); procs.append(cur)
    elif l == 'SPAWN' or l == 'BLOCK':
        j = lines.index('END', i)
        body = '\n'.join(lines[i + 1:j]) + '\n'
        if l == 'SPAWN':
            cur['spawn'] = body
        else:
            cur['blocks'].append(body)
        i = j
    elif l.startswith('X ') or l.startswith('ACT '):
        cur['ex'].append(l)
    i += 1
tot = bad = 0
td = Path(tempfile.mkdtemp())
for k, p in enumerate(procs):
    (td / 's').write_text(p['spawn']); (td / 'b').write_text('\n'.join(p['blocks'])); (td / 'e').write_text('\n'.join(p['ex']) + '\n')
    r = subprocess.run([str(exe), str(td / 's'), str(td / 'b'), str(td / 'e')], capture_output=True, text=True)
    t, b = map(int, r.stdout.split())
    tot += t; bad += b
    if t != len(p['blocks']):
        print('process', k, 'helper read', t, 'of', len(p['blocks']), r.stderr[:200])
print(f'helper-path parity: {tot - bad}/{tot} turns identical over {len(procs)} processes')
