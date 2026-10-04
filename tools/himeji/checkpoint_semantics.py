"""Demonstrate carried terminal queen lengths; read-only source check, no simulator."""
import argparse,hashlib,json,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();sys.path.insert(0,str(a.repo));from tools.s1.build import queen_cols
g={'rounds':[{0:('A',[(1,1),(1,2),(1,3)])},{0:('A',[(2,1),(1,1),(1,2)])}],'final':{'A':{'queen':3}}}
x={'source_sha256':hashlib.sha256((a.repo/'tools/s1/build.py').read_bytes()).hexdigest(),'last_recorded_round':1,'result':queen_cols(g,{'deaths':[]},'A'),'meaning':'q_len@490=3 is carried terminal length, not evidence of reaching490. Filter actual R>=490 before checkpoint inference.'};a.out.write_text(json.dumps(x,indent=2)+'\n');print(x)
