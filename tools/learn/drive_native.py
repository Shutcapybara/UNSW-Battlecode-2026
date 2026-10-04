"""Run the official engine in-process with natively compiled bots (one OS process per dragon, as on the judge) and
log every block each dragon received. Output feeds test_rebuild.py (block-rebuild parity on realistic games) and
encoder parity. Usage: python drive_native.py OUTDIR BOT_A BOT_B map[,map..] seed[,seed..]"""
import sys, subprocess, pickle, gzip, pathlib
from unswbc.engine import EngineModule

MAPS = pathlib.Path(__import__('unswbc').__file__).with_name('templates') / 'maps'


def run(bots, mapname, seed):
    E = EngineModule()
    procs, obs, spawn, deaths = {}, {}, {}, []

    def team_of(spawntxt):
        return spawntxt.split(b'TEAM ')[1][:1].decode()

    def on_spawn(did, s):
        spawn[did] = s
        p = subprocess.Popen([bots[team_of(s)]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        p.stdin.write(s); p.stdin.flush()
        procs[did] = p

    def reply(did, raw):
        obs.setdefault(did, []).append(raw)
        p = procs[did]
        try:
            p.stdin.write(raw + (b'' if raw.endswith(b'\n') else b'\n') + b'\n'); p.stdin.flush()
            out = []
            while True:
                ln = p.stdout.readline()
                if not ln:
                    break
                out.append(ln)
                if ln.strip() == b'ENDTURN':
                    break
            return b''.join(out)
        except BrokenPipeError:
            return b'ENDTURN\n'

    def on_death(did, rnd, reason):
        deaths.append((did, rnd, reason))
        p = procs.pop(did, None)
        if p:
            p.kill()

    res = E.run((MAPS / f'{mapname}.map').read_bytes(), reply, on_death=on_death, bot_spawn=on_spawn, debug=0, seed=seed)
    for p in procs.values():
        p.kill()
    return dict(map=mapname, seed=seed, bots=bots, result=res.__dict__, obs=obs, spawn=spawn, deaths=deaths,
                replay=E.replay(pathlib.Path(bots['A']).name, pathlib.Path(bots['B']).name))


if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    bots = {'A': sys.argv[2], 'B': sys.argv[3]}
    for m in sys.argv[4].split(','):
        for s in [int(v) for v in sys.argv[5].split(',')]:
            g = run(bots, m, s)
            with gzip.open(out / f'{m}-s{s}.truth.pkl.gz', 'wb') as f:
                pickle.dump(g, f)
            print(m, s, g['result']['rounds'], g['result']['winner'], 'blocks', sum(map(len, g['obs'].values())), flush=True)
