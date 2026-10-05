"""oracle test of a variant bed list on server games (kageyama, D-072 §E). usage: var_oracle.py VARMAP GAMES_FILE OUT part n budget
Re-runs the official engine (unswbc 1.2.9 engine module) on each server replay with the server seed, the replay's own
visible map lines and the variant's TILE lines; a game is reproduced when every dragon turn's block matches (0 mismatched,
0 extra engine turns)."""
import sys, json, os, time
sys.path.insert(0, 'tools/learn')
import oracle, rebuild
varmap, gfile, out, part, n, budget = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6])
beds = {}
for l in open(varmap):
    p = l.split()
    if p and p[0] == 'TILE' and p[3:] != ['0', '0']:
        beds[(int(p[1]), int(p[2]))] = (int(p[3]), int(p[4]))
def text_with(t):
    o = []
    for l in t.splitlines():
        p = l.split()
        if p and p[0] == 'TILE':
            c = (int(p[1]), int(p[2])); lo, hi = beds.get(c, (0, 0)); l = f'TILE {c[0]} {c[1]} {lo} {hi}'
        o.append(l)
    return '\n'.join(o) + ('\n' if t.endswith('\n') else '')
oracle.true_map = text_with
G = json.load(open(gfile))          # [[game, seed_hex], ...]
G = [g for g in G if g[0] % n == part]
fn = f'{out}.{part}.jsonl'; done = set()
if os.path.exists(fn): done = {json.loads(l)['game'] for l in open(fn)}
t0 = time.time(); f = open(fn, 'a'); k = 0
for g, s in G:
    if g in done: continue
    if time.time() - t0 > budget or k >= int(os.environ.get('CAP', '40')): break
    try:
        o = oracle.run(open(f'public_replays/corpus/replays/{g}.replay', 'rb').read(), int(s, 16))
        f.write(json.dumps(dict(game=g, turns=o['turns'], mism=o['mismatched'], extra=o['extra_engine_turns'], first=o['first'][:3] if o['first'] else None)) + '\n')
    except Exception as e:
        f.write(json.dumps(dict(game=g, err=str(e)[:200])) + '\n')
    k += 1; f.flush()
print(part, 'new', k, 'done', len(done) + k, 'of', len(G))
