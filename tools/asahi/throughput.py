#!/usr/bin/env python3
"""In-loop self-play throughput on the Mac (D-061 §C): official engine in-process + the legal encoder (tools/learn,
ENC_VERSION 1) + an untrained A10-shaped network (Hinata's r2_cnn.py: conv3x3 C->32, conv3x3 32->32, ReLU, flatten,
concat scalars, linear ->64, ReLU, linear ->4), numpy float32, batch 1 per decision (replies are synchronous).

Three modes, each on W worker processes for S seconds, games on the 17 live maps with varying seeds:
  engine  - trivial policy (keep facing): the engine + protocol floor
  encode  - + parse_block + Encoder.observe per decision
  net     - + the network forward and an action from its argmax (relative F/R/B/L -> absolute)
Reports decisions per second per worker, total decisions per hour, and games per hour. Entry bar (D-061 §C): 1e7/h.

    python tools/asahi/throughput.py [--workers 8] [--seconds 300] [--modes engine,encode,net]
"""
from __future__ import annotations

import argparse, json, os, random, sys, time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/learn'))
MAPS = ['schooltime', 'portals', 'slithery_fight', 'queen_of_spades', 'default', 'trophy', 'dilemma', 'autarky',
        'devil', 'trauma', 'australia', 'islands', 'unsw', 'maze', 'weakhold', 'stripes', 'tower_defense']
DIRS = 'NESW'


class Net:
    """Untrained A10-shaped network; weights from a fixed seed (the throughput, not the policy, is measured)."""

    def __init__(self, C, S, seed=7):
        import numpy as np
        self.np = np
        r = np.random.default_rng(seed)
        self.C, self.S = C, S
        self.w1 = (r.standard_normal((C * 9, 32)) * 0.05).astype(np.float32); self.b1 = np.zeros(32, np.float32)
        self.w2 = (r.standard_normal((32 * 9, 32)) * 0.05).astype(np.float32); self.b2 = np.zeros(32, np.float32)
        self.w3 = (r.standard_normal((32 * 49 + S, 64)) * 0.02).astype(np.float32); self.b3 = np.zeros(64, np.float32)
        self.w4 = (r.standard_normal((64, 4)) * 0.1).astype(np.float32); self.b4 = np.zeros(4, np.float32)
        # im2col gather indices for a 3x3 'same' conv on a zero-padded 9x9 grid
        idx = []
        for y in range(7):
            for x in range(7):
                idx.append([(y + dy) * 9 + (x + dx) for dy in range(3) for dx in range(3)])
        self.idx = np.array(idx)          # (49, 9)

    def conv(self, a, w, b):              # a: (Cin, 7, 7)
        np = self.np
        p = np.zeros((a.shape[0], 9, 9), np.float32)
        p[:, 1:8, 1:8] = a
        cols = p.reshape(a.shape[0], 81)[:, self.idx]          # (Cin, 49, 9)
        cols = cols.transpose(1, 0, 2).reshape(49, -1)          # (49, Cin*9)
        return np.maximum(cols @ w + b, 0).T.reshape(-1, 7, 7)  # (Cout, 7, 7)

    def __call__(self, planes, scalars):
        np = self.np
        h = self.conv(planes, self.w1, self.b1)
        h = self.conv(h, self.w2, self.b2)
        z = np.concatenate([h.reshape(-1), scalars])
        z = np.maximum(z @ self.w3 + self.b3, 0)
        return z @ self.w4 + self.b4


def worker(args):
    mode, seconds, wid = args
    import numpy as np
    import block as B
    import encode as E
    from unswbc.engine import EngineModule
    eng = EngineModule()
    net = Net(E.N_CH, E.N_SC) if mode == 'net' else None
    rng = random.Random(1000 + wid)
    t_end = time.time() + seconds
    decisions = games = 0
    t0 = time.time()
    while time.time() < t_end:
        m = rng.choice(MAPS)
        mb = (ROOT / 'maps/live' / f'{m}.map').read_bytes()
        enc = {}

        def spawn(d, s):
            if mode != 'engine':
                enc[d] = E.Encoder(B.parse_spawn(s.decode() if isinstance(s, bytes) else s))

        def reply(d, raw):
            nonlocal decisions
            if mode == 'engine':
                # facing is on the second line of the block: "DIR x"
                txt = raw.decode() if isinstance(raw, bytes) else raw
                if txt.startswith('ENDGAME'):
                    return b'ENDTURN\n'
                fac = txt.split('\n', 2)[1].split()[1]
                decisions += 1
                return f'MOVE {fac}\nPROTOCOL 3\nENDTURN\n'.encode()
            b = B.parse_block(raw)
            if b.ended:
                return b'ENDTURN\n'
            x = enc[d].observe(b)
            decisions += 1
            if mode == 'encode':
                rel = 'F'
            else:
                v = np.asarray(x, np.float32)
                planes = v[:49 * E.N_CH].reshape(49, E.N_CH).T.reshape(E.N_CH, 7, 7)
                scal = v[49 * E.N_CH:] * 0.01
                rel = 'FRBL'[int(np.argmax(net(planes, scal)))]
            enc[d].act('move', rel)
            absd = DIRS[(DIRS.index(b.dir) + 'FRBL'.index(rel)) % 4]
            return f'MOVE {absd}\nPROTOCOL 3\nENDTURN\n'.encode()

        eng.run(mb, reply, bot_spawn=spawn, debug=0, seed=rng.randrange(1, 2 ** 31))
        games += 1
    dt = time.time() - t0
    return dict(mode=mode, worker=wid, decisions=decisions, games=games, seconds=dt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--seconds', type=int, default=300)
    ap.add_argument('--modes', default='engine,encode,net')
    a = ap.parse_args()
    out = {}
    for mode in a.modes.split(','):
        with Pool(a.workers) as p:
            rows = p.map(worker, [(mode, a.seconds, i) for i in range(a.workers)])
        dec = sum(r['decisions'] for r in rows); sec = max(r['seconds'] for r in rows)
        g = sum(r['games'] for r in rows)
        out[mode] = dict(workers=a.workers, seconds=round(sec, 1), decisions=dec, games=g,
                         per_worker_per_s=round(dec / sec / a.workers, 1), per_hour=round(dec / sec * 3600),
                         games_per_hour=round(g / sec * 3600, 1), rows=rows)
        print(mode, json.dumps({k: v for k, v in out[mode].items() if k != 'rows'}), flush=True)
    import platform
    out['host'] = dict(node=platform.node(), cpu=platform.processor(), python=sys.version.split()[0],
                       cpus=os.cpu_count(), bar_per_hour=1e7)
    p = ROOT / 'docs/learning/results/asahi/throughput-d061c.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    print('wrote', p)


if __name__ == '__main__':
    main()
