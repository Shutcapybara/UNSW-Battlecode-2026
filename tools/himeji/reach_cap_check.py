"""Isolate the peer's BFS depth cap in a pure graph fixture, without importing query helpers."""
import argparse, ast, json, math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--peer',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
f=next(n for n in ast.parse(a.peer.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='bfs')
ns={};exec(compile(ast.Module(body=[f],type_ignores=[]),'<peer BFS>','exec'),ns)
graph={i:tuple(j for j in(i-1,i+1) if 0<=j<=14) for i in range(15)}
d=ns['bfs'](graph,0);out=[]
for L,target in [(9,10),(12,11),(12,12),(12,13)]:
    B=math.ceil(L/4)+L-2
    out.append(dict(length=L,target_distance=target,budget=B,peer_distance=d.get(target,99),peer_threat=d.get(target,99)<=B,correct_threat=target<=B))
assert all(x['peer_threat']==x['correct_threat'] for x in out[:2])
assert all(not x['peer_threat'] and x['correct_threat'] for x in out[2:])
a.out.write_text(json.dumps({'checks':out,'scope':'Pure source fixture, not measured incidence in selected replay cases; no simulator/policy run.'},indent=2)+'\n')
