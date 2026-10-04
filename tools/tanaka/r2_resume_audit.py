from pathlib import Path
import sys,types,runpy,tempfile,json
import numpy as np,pandas as pd
R=Path('/Users/alik/Documents/Projects/UNSW-Battlecode-2026');O=Path('/tmp/tanaka-r5')
# Fake backend performs no learning. Demonstrate cached model acceptance after changing rows/parameters.
counts={'train':0,'loaded':0};stub=types.ModuleType('lightgbm')
class Booster:
 def __init__(self,model_file=None):counts['loaded']+=int(model_file is not None)
 def predict(self,x):return np.tile([.7,.1,.1,.1],(len(x),1))
 def save_model(self,p):Path(p).write_text('synthetic model, no training')
stub.Booster=Booster;stub.Dataset=lambda *a,**kw:None
def train(*a,**kw):counts['train']+=1;return Booster()
stub.train=train;sys.modules['lightgbm']=stub
with tempfile.TemporaryDirectory(prefix='tanaka-resume-') as td:
 td=Path(td);df=pd.DataFrame([dict(game=str(i),side='A',dragon=0,round=1,series_key=str(i),map='Dev',split='train',y_kind=0,y_first=0,x_is_queen=1,x_cd_known=1,x_length=3) for i in range(2)]);df.to_parquet(td/'rows.parquet');pd.DataFrame([dict(game=str(i),side='A',team='7',weight=1.) for i in range(2)]).to_parquet(td/'t.parquet')
 argv=['r2_bc.py','fit','--rows',str(td/'rows.parquet'),'--teachers',str(td/'t.parquet'),'--cv','game','--run',str(td/'run'),'--rounds','400'];sys.argv=argv;runpy.run_path(str(R/'tools/hinata/r2_bc.py'),run_name='__main__');first=counts.copy();reg1=json.loads((td/'run/registry.json').read_text());df.x_length=99;df.to_parquet(td/'rows.parquet');sys.argv=argv[:-1]+['800'];runpy.run_path(str(R/'tools/hinata/r2_bc.py'),run_name='__main__');reg2=json.loads((td/'run/registry.json').read_text())
 out={'backend':'fake; no model fit or teacher-data read','first_counts':first,'after_changed_rows_and_rounds':counts,'additional_train_calls':counts['train']-first['train'],'registered_rounds':reg2['rounds'],'registered_new_data_hash':reg2['rows_sha']!=reg1['rows_sha'],'cached_files_reused':counts['train']==first['train']}
(O/'resume-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
