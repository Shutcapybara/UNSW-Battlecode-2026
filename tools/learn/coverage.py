"""Oracle coverage of a frozen cohort, label-free in its output: per game only whether the engine re-run (server seed +
template beds) reproduces the replay turn for turn, the number of turns, and the number of teacher-side processes.
No action, label, outcome or feature value is written. Resumable (appends JSON lines; skips games already present).
    python coverage.py COHORT.parquet REPLAY_DIR GAMES.parquet OUT.jsonl [MAX_GAMES]"""
import sys, json, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
import oracle, rebuild

coh, rdir, games_f, out = sys.argv[1:5]
cap = int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 9
C = pd.read_parquet(coh)
seeds = dict(zip(*pd.read_parquet(games_f, columns=['game', 'seed']).astype(str).values.T))
done = set()
if Path(out).exists():
    done = {json.loads(l)['game'] for l in open(out)}
n = 0
with open(out, 'a') as f:
    for r in C.itertuples():
        if r.game in done or n >= cap:
            continue
        data = (Path(rdir) / f'{r.game}.replay').read_bytes()
        res = oracle.run(data, int(seeds[r.game], 16), keep=False)
        sides = set(r.teacher_sides.split(','))
        procs = collections.Counter()
        rebuild.walk(data, lambda i, sp, txt, ctx: procs.__setitem__((sp['team'], i), 1))
        f.write(json.dumps(dict(game=r.game, map=r.map, series_key=r.series_key, reproduced=bool(res['mismatched'] == 0 and res['extra_engine_turns'] == 0),
                                turns=res['turns'], teacher_sides=r.teacher_sides,
                                teacher_processes=sum(1 for (t, _) in procs if t in sides))) + '\n')
        f.flush(); n += 1
