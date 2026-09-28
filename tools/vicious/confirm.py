"""One-worker confirmation queue; selection rule pre-registered in BROAD_DESIGN."""
import json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
C=Path(json.loads((ROOT/'tools/vicious/current.json').read_text())['directory'])

def wait_rows(path,n):
    while not path.exists() or len(json.loads(path.read_text()))<n:time.sleep(4)

def run(name,arms,opps,maps,fast=True,sandbox=False,reuse=()):
    cmd=[str(ROOT/'.venv/bin/python'),str(ROOT/'tools/vicious/panel.py'),str(C/name),'--jobs','1','--arms',*arms,'--opps',*opps,'--maps',*maps]
    if fast:cmd+=['--fast']
    if sandbox:cmd+=['--sandbox']
    for p in reuse:cmd+=['--reuse-panel',str(C/p)]
    subprocess.run(cmd,cwd=ROOT,check=True)

wait_rows(C/'cycle_04/components/results.json',48)
rows=[]
for folder in ('cycle_02/accelerated','cycle_03/crown_guard','cycle_04/components'):
    rows+=json.loads((C/folder/'results.json').read_text())
order=json.loads((C/'cycle_04/BROAD_DESIGN.json').read_text())['selection_tie_order']
scores={a:sum(r['outcome']==r['side'] for r in rows if r['arm']==a) for a in order}
eligible=[a for a in order if scores[a]>=9]
assert eligible, scores
candidate=max(eligible,key=lambda a:scores[a])
selection_path=C/'release/SELECTION.json'
if selection_path.exists():
    selection=json.loads(selection_path.read_text());candidate=selection['candidate']
else:
    selection={'candidate':candidate,'scores':scores,'rule':'Most fixed-screen wins; pre-registered order breaks ties; minimum9/16. Guard excluded without benefit.','selected_at':time.time(),'frozen_before_broad_outcomes':True}
    selection_path.write_text(json.dumps(selection,indent=2)+'\n')
print('Selected',selection,flush=True)
wait_rows(C/'cycle_04/late_activation/results.json',24)
maps=list(json.loads((C/'baseline/experiment_data__bot-ratings__latest.json').read_text())['map_weights'])
parent='vicious-v01-frozen';opps=['newton-x10-candidate','gavroche-v32-supported-divecap']
reuse=['cycle_01/control_seeded','cycle_02/accelerated','cycle_03/body_control','cycle_03/crown_guard','cycle_03/late','cycle_04/components','cycle_04/late_activation']
run('cycle_04/broad',[parent,candidate],opps,maps,reuse=reuse)
reserve=json.loads((C/'RESERVE_LEDGER.json').read_text())['family_confirmation_reserved']
run('cycle_04/opponent_reserve',[parent,candidate],['valjean-v01-portal-memory'],reserve)
run('release/native',[candidate],['gavroche-v32-supported-divecap'],['md26_orchard_narrow_s0','big_empty'],fast=False)
run('release/native_valjean',[candidate],['valjean-v01-portal-memory'],['mc26_crossroads'],fast=False)
os.environ['XDG_CACHE_HOME']='/private/tmp/vicious-cache'
run('release/sandbox',[candidate],[parent],['big_empty','trauma','md26_orchard_narrow_s0'],fast=False,sandbox=True)
print('Confirmation queue complete.',flush=True)
