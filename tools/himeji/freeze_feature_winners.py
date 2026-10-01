"""Freeze only old feature outcomes for parity; never invokes the feature extractor."""
import argparse,hashlib,json
from pathlib import Path
import pandas as pd

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 rows=[];manifest={}
 for bot in ['kyoto-01-nodevil','kyoto-03-latecap']:
  for panel in ['pool','gen']:
   fs=sorted((a.runs/bot/panel).glob('features*/features.parquet'))
   for f in fs: manifest[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
   df=pd.concat([pd.read_parquet(f,columns=['game','side','bot','opponent','result']) for f in fs],ignore_index=True).drop_duplicates(['game','side'])
   df=df[df.bot==bot].copy();df['panel']=panel;rows+=df.to_dict('records')
 (a.out/'feature-winners.json').write_text(json.dumps(rows)+'\n')
 (a.out/'feature-source-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
