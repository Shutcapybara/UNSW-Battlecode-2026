"""Find the first gameplay divergence in two retained, successful fixture replays."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT))
from tools.learn.rebuild import walk

def read(run,fixture):
    path=MAIN/'build/kenma'/run/(fixture+'.replay')
    result=json.loads(path.with_suffix('.json').read_text())
    assert result['rc']==0 and not result['faults'] and result['winner']
    rows=[]
    def emit(ident,spawn,block,ctx):
        lines=block.splitlines()
        units=int(next(x for x in lines if x.startswith('UNIT_COUNT ')).split()[1])
        messages=int(next(x for x in lines if x.startswith('NUM_MSGS ')).split()[1])
        rays=ctx['sonar'];tag=0xd3 if spawn['team']=='A' else 0x69
        flagged=any(((v['value']>>8)&8) and (v['value']&255)==tag for v in rays)
        rows.append(dict(id=ident,team=spawn['team'],round=ctx['round'],action=ctx['action'],
                         head=ctx['head'],length=ctx['length'],units=units,messages=messages,
                         rays=len(rays),outbound_proof=flagged))
    walk(path.read_bytes(),emit)
    return result,rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('first');ap.add_argument('second')
    ap.add_argument('fixture');ap.add_argument('--output',required=True);a=ap.parse_args()
    ra,first=read(a.first,a.fixture);rb,second=read(a.second,a.fixture)
    assert all(ra[k]==rb[k] for k in ['map','seed','opp','seat'])
    keys=['id','round','action','head','length','units']
    index=next((i for i,(x,y) in enumerate(zip(first,second)) if any(x[k]!=y[k] for k in keys)),min(len(first),len(second)))
    proof={};unflagged=[]
    for row in second:
        if row['team']!=rb['seat']:continue
        if row['outbound_proof']:proof.setdefault(row['id'],row['round'])
        elif row['units']>=63:unflagged.append(row)
    report=dict(first_run=a.first,second_run=a.second,fixture=a.fixture,
                compared_fields=keys,first_divergence_index=index,
                first_context=first[max(0,index-3):index+5],second_context=second[max(0,index-3):index+5],
                first_outbound_proof=proof,unflagged_at_units63_or_more=len(unflagged),
                unflagged_examples=unflagged[:20],turn_counts=[len(first),len(second)],
                note='Outbound proof marker is a radio observation, not direct access to process state. A process with no rays may know the proof without showing it here.')
    (MAIN/'build/kenma'/a.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['first_context','second_context','first_outbound_proof','unflagged_examples']}))

if __name__=='__main__':main()
