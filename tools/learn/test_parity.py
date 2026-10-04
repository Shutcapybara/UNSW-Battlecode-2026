"""Python = C++ encoder parity (R0 gate: bit for bit on >= 1,000 turns). Writes the fixture, compiles and runs
cpp/parity_main.cpp.  python3 tools/learn/test_parity.py [--min-turns 1000] truth.pkl.gz ... | replay files"""
import sys, gzip, pickle, random, subprocess, tempfile, collections
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import block as B, encode as E, labels as LB, rebuild

KIND = {0: 1, 1: 2, 2: 3, 3: 0}


def processes_from_truth(path):
    g = pickle.load(gzip.open(path))
    acts = collections.defaultdict(list)
    rebuild.walk(g['replay'], lambda i, sp, txt, ctx: acts[i].append(ctx))
    for did, blocks in g['obs'].items():
        yield g['spawn'][did].decode(), [(raw.decode(), acts[did][k] if k < len(acts[did]) else None) for k, raw in enumerate(blocks)]


def processes_from_replay(path):
    seqs = collections.defaultdict(list); spawns = {}
    def em(i, sp, txt, ctx):
        spawns[i] = f"ID {sp['id']}\nTEAM {sp['team']}\nMAP {sp['W']} {sp['H']}\nUNIT_LIMIT {sp['unit_limit']}\n"
        seqs[i].append((txt, ctx))
    rebuild.walk(Path(path).read_bytes(), em)
    for i in seqs:
        yield spawns[i], seqs[i]


def main():
    args = sys.argv[1:]
    min_turns = 1000
    if args and args[0].startswith('--min-turns='):
        min_turns = int(args.pop(0).split('=')[1])
    procs = []
    for p in args:
        gen = processes_from_truth(p) if p.endswith('.pkl.gz') else processes_from_replay(p)
        procs += list(gen)
    random.Random(7).shuffle(procs)
    out, n = [], 0
    for sp_txt, seq in procs:
        if n >= min_turns:
            break
        enc = E.Encoder(B.parse_spawn(sp_txt))
        out.append('PROC'); out.append('SPAWN'); out.append(sp_txt.strip()); out.append('END')
        for raw, ctx in seq:
            b = B.parse_block(raw)
            x = enc.observe(b)
            out += ['BLOCK', B.canon(raw).strip(), 'END', 'X ' + ' '.join(map(str, x))]
            if ctx is not None:
                y = LB.label(ctx, b)
                kind = KIND[y['y_kind']]
                enc.act({1: 'move', 2: 'split', 3: 'invalid', 0: 'none'}[kind], list(y['y_seq']) if kind == 1 else None,
                        rnd=ctx['round'])
                out.append(f"ACT {kind} {y['y_first'] if kind == 1 else -1} {y['y_nsteps'] if kind == 1 else 0} {ctx['round']}")
            n += 1
    fx = Path(tempfile.gettempdir()) / 'learn_parity_fixture.txt'
    fx.write_text('\n'.join(out) + '\n')
    exe = Path(tempfile.gettempdir()) / 'learn_parity'
    subprocess.run(['g++', '-std=c++20', '-O2', '-o', str(exe), str(HERE / 'cpp' / 'parity_main.cpp')], check=True)
    r = subprocess.run([str(exe)], stdin=open(fx), capture_output=True, text=True)
    print(r.stdout.strip()); print(r.stderr.strip()[:2000])
    print('python turns', n, 'fixture', fx)
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
