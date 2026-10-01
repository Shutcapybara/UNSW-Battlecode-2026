# Throughput probe: the official unswbc 1.2.3 wasm engine in-process with a Python per-dragon callback (antioch, H-RL1).
# Run from the worktree root: python3 tools/antioch/rl/engine_bench.py
import sys, time, random
sys.path.insert(0, '../UNSW-Battlecode-2026/.venv/lib/python3.12/site-packages')
from unswbc.engine import EngineModule
E = EngineModule()
OFF = {b'N': (0, -1), b'E': (1, 0), b'S': (0, 1), b'W': (-1, 0)}
def reply_factory():
    calls = [0]; t_pol = [0.0]
    def reply(did, obs):
        t0 = time.perf_counter(); calls[0] += 1
        occ = set(); head = None
        for ln in obs.split(b'\n'):
            p = ln.split()
            if len(p) == 6 and p[0][:1].isalpha():
                x, y = int(p[2]), int(p[3]); occ.add((x, y))
                if int(p[1]) == did and p[5] == b'1': head = (x, y)
        ds = list(OFF); random.shuffle(ds); mv = ds[0]
        if head:
            for d in ds:
                o = OFF[d]
                if (head[0] + o[0], head[1] + o[1]) not in occ: mv = d; break
        t_pol[0] += time.perf_counter() - t0
        return b'MOVE ' + mv + b'\n'
    return reply, calls, t_pol
tot_c = tot_t = tot_p = 0
for m in ['default', 'trophy', 'big_empty', 'portals', 'trauma', 'schooltime']:
    reply, calls, tp = reply_factory()
    t = time.time(); r = E.run(open(f'maps/{m}.map', 'rb').read(), reply, debug=0, seed=1); dt = time.time() - t
    tot_c += calls[0]; tot_t += dt; tot_p += tp[0]
    print(f'{m:12s} rounds {r.rounds:3d} decisions {calls[0]:6d} {dt:6.2f}s  {calls[0]/dt:8,.0f}/s  (python policy {tp[0]/dt:.0%})')
print(f'total {tot_c} decisions in {tot_t:.1f}s = {tot_c/tot_t:,.0f}/s per core; engine-only ≈ {tot_c/(tot_t-tot_p):,.0f}/s')
