"""Execute only peer queen_cols on synthetic and one frozen replay boundary; read-only."""
import argparse, ast, hashlib, json, subprocess, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('--repo', type=Path, required=True)
ap.add_argument('--lineage', type=Path, required=True)
ap.add_argument('--index', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
src = subprocess.check_output(['git', 'show', '24ea5e539:tools/s1/build.py'], cwd=a.lineage, text=True)
fn = next((n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == 'queen_cols'))
ns = {'Q_ROUNDS': [490]}
exec(compile(ast.Module(body=[fn], type_ignores=[]), 'peer_queen_cols', 'exec'), ns)
rows = []
for last in [488, 489, 490]:
    snap = {0: ('A', ((0, 0), (1, 0), (2, 0)))}
    g = {'rounds': [snap] * (last + 2), 'last_round': last, 'final': {'A': {'queen': 3}}}
    z = ns['queen_cols'](g, {'deaths': []}, 'A')
    rows.append({'actual_last_round': last, 'snapshot_count': len(g['rounds']), 'reported_q_len490': z['q_len@490'], 'reported_q_censored': z['q_censored'], 'expected_reach': last >= 490, 'expected_q_len490': 3 if last >= 490 else None})
sys.path.insert(0, str(a.repo))
from tools.analysis.features import frame as F
meta = next((r for r in map(json.loads, a.index.read_text().splitlines()) if r['game_id'] == 867918))
p = a.repo / 'public_replays/corpus/replays/867918.replay'
assert hashlib.sha256(p.read_bytes()).hexdigest() == meta['sha256']
g = F.decode(p)
assert g['winner'].lower() == meta['winner']
real = []
for side in ['A', 'B']:
    z = ns['queen_cols'](g, {'deaths': []}, side)
    real.append({'side': side, 'actual_last_round': g['last_round'], 'snapshot_count': len(g['rounds']), 'reported_q_len490': z['q_len@490'], 'reported_q_censored': z['q_censored'], 'header_queen': g['final'][side]['queen'], 'actual_reached490': g['last_round'] >= 490})
out = {'source_commit': '24ea5e539', 'source_sha256': hashlib.sha256(src.encode()).hexdigest(), 'function_source': ast.get_source_segment(src, fn), 'synthetic_rows': rows, 'live_boundary_game': meta, 'live_result': real, 'scope': 'Synthetic alive-end boundary plus one existing ranked Default replay. Other stores not rewritten.'}
a.out.write_text(json.dumps(out, indent=2) + '\n')
print(real)
