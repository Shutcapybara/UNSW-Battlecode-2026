"""Package and parity-check the existing coherent-teacher model; no fit or bot mutation."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,zipfile,re
import numpy as np
import pyarrow.parquet as pq
import lightgbm as lgb
ROOT=Path(__file__).resolve().parents[2];MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path[:0]=[str(ROOT/'tools/learn'),str(ROOT/'tools/kenma')]
import export_gbt
import lgb_missing
from panel import check_space
assert os.getpriority(os.PRIO_PROCESS,0)>=15;check_space()
src=MAIN/'build/learn/hinata/r2full/A1-team213';out=MAIN/'build/kenma/teacher213';out.mkdir(exist_ok=True)
raw=(src/'model_all_400.txt').read_bytes();sha=hashlib.sha256(raw).hexdigest();(out/'model_all_400.txt').write_bytes(raw)
manifest=json.loads((src/'manifest.json').read_text());assert manifest['team']=='213' and manifest['rounds']==400 and manifest['n_features']==270
shard=next((MAIN/'build/learn/kageyama/teachers_v1').glob('*.parquet'))
features=[c for c in pq.read_schema(shard).names if c.startswith('hb_f_')]
header=(ROOT/'bots/carthage-05-free-sprint/hb1_direction_compact.hpp').read_text();names=re.findall(r'"([^"]*)"',re.search(r'dirc_feats\[\] = \{([^}]*)\}',header).group(1))
assert features==['hb_f_'+x for x in names] and len(features)==270
model=lgb.Booster(model_file=str(out/'model_all_400.txt'));assert model.current_iteration()==400 and model.num_feature()==270
packed,missing=lgb_missing.from_lgb(str(out/'model_all_400.txt'))
info=export_gbt.emit(packed,str(out/'teacher213.hpp'),'teacher213')
shutil.copy2(ROOT/'tools/learn/cpp/gbt_compact.hpp',out/'gbt_compact.hpp')
# A bounded real observation slice, plus finite and missing-value edge cases.
batch=next(pq.ParquetFile(shard).iter_batches(batch_size=2048,columns=features));x=np.column_stack([batch.column(i).to_numpy(zero_copy_only=False) for i in range(270)]).astype(np.float32)
single=np.repeat(x[:1],270,axis=0);single[np.arange(270),np.arange(270)]=np.nan
rng=np.random.default_rng(213);masked=x[:512].copy();masked[rng.random(masked.shape)<0.25]=np.nan
x=np.concatenate([x,single,masked,np.zeros((1,270),np.float32),np.full((1,270),np.nan,np.float32)])
x.tofile(out/'features.f32');expected=model.predict(x,num_threads=1);assert expected.shape==(len(x),4)
(out/'check.cpp').write_text('''#include <fstream>\n#include <array>\n#include "gbt_compact.hpp"\n#include "teacher213.hpp"\nint main(int argc,char**argv){std::ifstream in(argv[1],std::ios::binary);std::ofstream out(argv[2],std::ios::binary);std::array<float,270>x;double p[4];while(in.read((char*)x.data(),sizeof(x))){GBT_PROBA(teacher213,x.data(),p);out.write((char*)p,sizeof(p));}return in.eof()?0:1;}\n''')
subprocess.run(['clang++','-O2','-std=c++20',str(out/'check.cpp'),'-o',str(out/'check')],check=True)
subprocess.run([str(out/'check'),str(out/'features.f32'),str(out/'native.f64')],check=True)
actual=np.fromfile(out/'native.f64',dtype=np.float64).reshape(-1,4);assert actual.shape==expected.shape
error=float(np.max(np.abs(actual-expected)));same=int(np.sum(actual.argmax(1)==expected.argmax(1)));assert error<1e-6 and same==len(x)
with zipfile.ZipFile(out/'model.zip','w',zipfile.ZIP_DEFLATED) as z:z.write(out/'teacher213.hpp','teacher213.hpp')
report=dict(source=str(src),source_sha256=sha,source_manifest=manifest,export=info,missing_semantics=missing,features=features,parity_rows=len(x),max_probability_error=error,argmax_equal=same,model_zip_bytes=(out/'model.zip').stat().st_size,note='No refit, no gameplay measurements. Tested real observation slice,270 single-feature NaNs,512 random missing-feature masks and zero/all-NaN vectors. Future use must verify runtime feature binding, exact combined zip and sandbox compute.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('features','source_manifest')}),flush=True)
