#!/usr/bin/env python3
"""In-loop self-play throughput on the Mac (D-061 §C): official engine in-process + the legal encoder (tools/learn,
ENC_VERSION 1) + an untrained A10-shaped network (Hinata's r2_cnn.py: conv3x3 C->32, conv3x3 32->32, ReLU, flatten,
concat scalars, linear ->64, ReLU, linear ->4), numpy float32, batch 1 per decision (replies are synchronous).

Three modes, each on W worker processes for S seconds, games on the 17 live maps with varying seeds:
  engine  - trivial policy (keep facing): the engine + protocol floor
  encode  - + parse_block + Encoder.observe per decision
  net     - + the network forward and an action from its argmax (relative F/R/B/L -> absolute)
Reports decisions per second per worker, total decisions per hour, and games per hour. Entry bar (D-061 §C): 1e7/h.

    python tools/asahi/throughput.py [--workers 8] [--seconds 300] [--chunk 30] [--max-games 500] [--modes engine,encode,net]

Each task runs in a fresh process (maxtasksperchild=1): per-game wasmtime stores leak address space (jobs 176-178).
Wall-clock rates include process start-up; per-decision times split engine+glue / encoder / network.
"""
from __future__ import annotations

import argparse, gc, json, os, random, sys, time, traceback
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
    """Returns plain numbers only. Any exception (including one the engine re-raises from a callback as a wasmtime
    trap, which holds ctypes pointers and cannot cross processes: job 172) comes back as a traceback string, with the
    progress made before it."""
    prog = {}
    try:
        return _worker(args, prog)
    except BaseException:
        mode, seconds, wid, max_games = args
        return dict(mode=mode, worker=wid, **prog, error=traceback.format_exc()[-4000:])


def _worker(args, prog):
    mode, seconds, wid, max_games = args
    import numpy as np
    import block as B
    import encode as E
    from unswbc.engine import EngineModule
    eng = EngineModule()
    net = Net(E.N_CH, E.N_SC) if mode == 'net' else None
    rng = random.Random(1000 + wid)
    pc = time.perf_counter
    t_end = time.time() + seconds
    st = dict(decisions=0, games=0, rounds=0, t_cb=0.0, t_enc=0.0, t_net=0.0, seconds=0.0)
    prog.update(st)
    cb_err = []
    t0 = time.time()
    # at least one game (the in-process smoke uses seconds = 0); at most max_games per process: wasmtime stores leak
    # address space per game (jobs 176-178: instantiate fails with ENOMEM after many short games even with
    # gc.collect every 4 games), so rollout processes must be recycled (Pool maxtasksperchild=1 in main)
    while st['games'] == 0 or (time.time() < t_end and st['games'] < max_games):
        m = rng.choice(MAPS)
        mb = (ROOT / 'maps/live' / f'{m}.map').read_bytes()
        enc = {}

        def spawn(d, s):
            try:
                if mode != 'engine':
                    enc[d] = E.Encoder(B.parse_spawn(s.decode() if isinstance(s, bytes) else s))
            except Exception:
                cb_err.append(traceback.format_exc()[-4000:])

        def reply(d, raw):
            c0 = pc()
            try:
                return _reply(d, raw)
            except Exception:
                cb_err.append(traceback.format_exc()[-4000:])
                return b'ENDTURN\n'
            finally:
                st['t_cb'] += pc() - c0

        def _reply(d, raw):
            if mode == 'engine':
                # facing is on the second line of the block: "DIR x"
                txt = raw.decode() if isinstance(raw, bytes) else raw
                if txt.startswith('ENDGAME'):
                    return b'ENDTURN\n'
                fac = txt.split('\n', 2)[1].split()[1]
                st['decisions'] += 1
                return f'MOVE {fac}\nPROTOCOL 3\nENDTURN\n'.encode()
            c0 = pc()
            b = B.parse_block(raw)
            if b.ended:
                return b'ENDTURN\n'
            x = enc[d].observe(b)
            c1 = pc()
            st['t_enc'] += c1 - c0
            st['decisions'] += 1
            if mode == 'encode':
                rel = 'F'
            else:
                v = np.asarray(x, np.float32)
                planes = v[:49 * E.N_CH].reshape(49, E.N_CH).T.reshape(E.N_CH, 7, 7)
                scal = v[49 * E.N_CH:] * 0.01
                rel = 'FRBL'[int(np.argmax(net(planes, scal)))]
                st['t_net'] += pc() - c1
            enc[d].act('move', rel)
            absd = DIRS[(DIRS.index(b.dir) + 'FRBL'.index(rel)) % 4]
            return f'MOVE {absd}\nPROTOCOL 3\nENDTURN\n'.encode()

        res = eng.run(mb, reply, bot_spawn=spawn, debug=0, seed=rng.randrange(1, 2 ** 31))
        st['games'] += 1
        st['rounds'] += int(res.rounds)
        eng._live = None
        if st['games'] % 4 == 0:
            gc.collect()
        st['seconds'] = time.time() - t0
        prog.update(st)
        if cb_err:
            raise RuntimeError(f'callback failed on {m}:\n' + cb_err[0])
    st['seconds'] = time.time() - t0
    return dict(mode=mode, worker=wid, **st)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--seconds', type=int, default=300)
    ap.add_argument('--chunk', type=int, default=30, help='seconds per task; each task runs in a fresh process')
    ap.add_argument('--max-games', type=int, default=500, help='games per task at most (address-space leak)')
    ap.add_argument('--modes', default='engine,encode,net')
    a = ap.parse_args()
    out = {}
    for mode in a.modes.split(','):
        smoke = worker((mode, 0, -1, 1))      # one game in-process first: a failure prints its full traceback here
        print('smoke', mode, json.dumps(smoke), flush=True)
        if smoke.get('error'):
            out[mode] = dict(error=smoke['error'])
            continue
        n = a.workers * max(1, -(-a.seconds // a.chunk))
        w0 = time.time()
        with Pool(a.workers, maxtasksperchild=1) as p:
            rows = list(p.imap_unordered(worker, [(mode, a.chunk, i, a.max_games) for i in range(n)]))
        wall = time.time() - w0
        errs = [r for r in rows if r.get('error')]
        if errs:
            print(mode, 'task errors', len(errs), 'of', n, 'games before error', [r.get('games') for r in errs][:8],
                  errs[0]['error'], flush=True)
        dec = sum(r.get('decisions', 0) for r in rows); g = sum(r.get('games', 0) for r in rows)
        busy = sum(r.get('seconds', 0.0) for r in rows)
        t_cb = sum(r.get('t_cb', 0.0) for r in rows); t_enc = sum(r.get('t_enc', 0.0) for r in rows)
        t_net = sum(r.get('t_net', 0.0) for r in rows)
        us = lambda t: round(1e6 * t / max(dec, 1), 1)
        out[mode] = dict(workers=a.workers, tasks=n, task_errors=len(errs), wall_seconds=round(wall, 1), decisions=dec,
                         games=g, per_hour=round(dec / wall * 3600), games_per_hour=round(g / wall * 3600, 1),
                         mean_rounds=round(sum(r.get('rounds', 0) for r in rows) / max(g, 1), 1),
                         decisions_per_game=round(dec / max(g, 1), 1),
                         us_per_decision_core_wall=round(1e6 * wall * a.workers / max(dec, 1), 1),
                         us_per_decision_core_busy=us(busy), us_engine_and_glue=us(busy - t_cb + (t_cb - t_enc - t_net)),
                         us_encoder=us(t_enc), us_net=us(t_net), process_overhead_share=round(1 - busy / (wall * a.workers), 3),
                         smoke=smoke, rows=rows)
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
