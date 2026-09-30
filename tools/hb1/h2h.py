"""HB-1 head-to-head runner: one arm vs one opponent on a map set, both seats, fixed seeds (native unswbc).

    .venv/bin/python tools/hb1/h2h.py --arm bots/hb1-01-structured --opp bots/ares-v04-tyr12-behavior-parity \
        [--maps live] [--seeds 2] [--jobs 8] [--out NAME]

--maps live = the ten live maps Heartbreaker played our Ares V04 on (29 Sep). Seeds derive from (map, seat, k) so
every arm meets the same fixtures. Resumable: finished fixtures in the output are skipped.
Writes game_stats/runs/hb1-h2h-<NAME>.json.
"""
import argparse, hashlib, json, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ['autarky', 'default', 'devil', 'dilemma', 'portals', 'queen_of_spades', 'schooltime', 'slithery_fight',
        'trauma', 'trophy']
RX = re.compile(r'team (A|B) wins after (\d+) rounds \(([^)]*)\)')


def run(fx, arm, opp, rdir):
    mp, seat, k = fx
    seed = int(hashlib.sha256(f'{mp}|{seat}|{k}'.encode()).hexdigest()[:6], 16)
    a, b = (arm, opp) if seat == 'A' else (opp, arm)
    rp = rdir / f'{mp}__{seat}__{k}.replay'
    t = time.time()
    p = subprocess.run([str(ROOT / '.venv/bin/unswbc'), 'run', str(ROOT / 'maps' / f'{mp}.map'), str(ROOT / a),
                        str(ROOT / b), '-o', str(rp), '--seed', str(seed), '--no-logs', '--no-draw'],
                       capture_output=True, text=True, timeout=3600, cwd=ROOT)
    tail = (p.stdout + p.stderr)[-2000:]
    m = RX.search(tail)
    if m:
        w, rounds, how = m.group(1), int(m.group(2)), m.group(3)
        res = 'W' if w == seat else 'L'
    else:
        w, rounds, how = ('draw' if 'draw' in tail.lower() else 'error'), None, tail.strip().splitlines()[-1][-150:]
        res = w
    return dict(map=mp, seat=seat, k=k, seed=seed, result=res, rounds=rounds, how=how, secs=round(time.time() - t))


def prebuild(bots):
    """Build each bot once, serially, before parallel games (concurrent `unswbc run`s race on .unswbc-build;
    same fix as origin/main tools/analysis/features/run_panel.py)."""
    from unswbc.project import Project
    for b in bots:
        t = time.time()
        Project.from_dir(ROOT / b).compile()
        print(f'built {b} in {time.time() - t:.0f}s', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--opp', required=True)
    ap.add_argument('--maps', default='live')
    ap.add_argument('--seeds', type=int, default=2)
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    maps = LIVE if a.maps == 'live' else a.maps.split(',')
    out = ROOT / 'game_stats' / 'runs' / f'hb1-h2h-{a.out}.json'
    rdir = ROOT / 'build' / 'hb1' / 'games' / a.out
    rdir.mkdir(parents=True, exist_ok=True)
    rows = json.loads(out.read_text())['games'] if out.exists() else []
    done = {(r['map'], r['seat'], r['k']) for r in rows if r['result'] in ('W', 'L', 'draw')}
    fixtures = [(m, s, k) for m in maps for s in 'AB' for k in range(a.seeds) if (m, s, k) not in done]
    rows = [r for r in rows if (r['map'], r['seat'], r['k']) in done]

    def save():
        w = sum(r['result'] == 'W' for r in rows)
        n = sum(r['result'] in ('W', 'L', 'draw') for r in rows)
        out.write_text(json.dumps(dict(arm=a.arm, opp=a.opp, maps=maps, seeds=a.seeds, played=n, wins=w,
                                       win_rate=w / max(1, n), games=rows), indent=1))
        return w, n

    prebuild([a.arm, a.opp])
    with ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(lambda f: run(f, a.arm, a.opp, rdir), fixtures):
            rows.append(r)
            w, n = save()
            print(f"{r['map']:16s} {r['seat']} k{r['k']} {r['result']} r{r['rounds']} {r['how']:14s} {r['secs']}s  "
                  f"[{w}/{n}]", flush=True)
    w, n = save()
    print(f'{a.arm} vs {a.opp}: {w}/{n} = {w / max(1, n):.3f}')


if __name__ == '__main__':
    main()
