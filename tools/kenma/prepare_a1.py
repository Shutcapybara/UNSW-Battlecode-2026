"""Build Kenma 02 from the archived A1 fold-0 direction model, without refitting."""
from pathlib import Path
import hashlib
import io
import json
import shutil
import sys
import tarfile
import zipfile
import lightgbm as lgb
import pyarrow.parquet as pq
import re

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT/'tools/learn'))
import export_gbt
src=MAIN/'build/hinata/r2/battery/A1-u'
out=MAIN/'build/kenma/a1'
out.mkdir(parents=True,exist_ok=True)
raw=b''.join(p.read_bytes() for p in sorted(src.glob('models.tgz.part_*')))
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
    member=next(m for m in archive.getmembers() if Path(m.name).name=='model_f0.txt')
    data=archive.extractfile(member).read()
expected=(src/'models.sha256').read_text().splitlines()[0].split()[0]
assert hashlib.sha256(data).hexdigest()==expected
(out/'model_f0_800.txt').write_bytes(data)
model=lgb.Booster(model_file=str(out/'model_f0_800.txt'))
model.save_model(str(out/'model_f0_400.txt'),num_iteration=400)
# The original fit received a numpy matrix, so the model stores Column_N names.
# Recover the order from its input parquet schema, as r2_battery.get/cols did.
shard=next((MAIN/'build/learn/kageyama/hb1_dev120').glob('*.parquet'))
features=[c for c in pq.read_schema(shard).names if c.startswith('hb_f_')]
old_header=(ROOT/'bots/carthage-05-free-sprint/hb1_direction_compact.hpp').read_text()
old_feats=re.findall(r'"([^"]*)"', re.search(r'dirc_feats\[\] = \{([^}]*)\}',old_header).group(1))
assert features==['hb_f_'+f for f in old_feats]
assert len(features)==270 and all(f.startswith('hb_f_') for f in features)
(out/'features.txt').write_text('\n'.join(features)+'\n')
dst=ROOT/'bots/kenma-02-topteam-prior'
shutil.copytree(ROOT/'bots/carthage-05-free-sprint',dst,ignore=shutil.ignore_patterns('.unswbc-build','__pycache__','CANDIDATE.toml','hb1_direction_compact.hpp'))
shutil.copy2(ROOT/'tools/learn/cpp/gbt_compact.hpp',dst/'gbt_compact.hpp')
info=export_gbt.emit(export_gbt.from_lgb(str(out/'model_f0_400.txt')),str(dst/'kenma_model.hpp'),'kenma_model')
names=',\n'.join(json.dumps(f.removeprefix('hb_f_')) for f in features)
(dst/'hb1_compact.hpp').write_text('''// Kenma 02: top-ten pooled A1-400 fold-0 prior on HB-1 features.\n#pragma once\n#include <cmath>\n#include <vector>\n#include "hb1_models.hpp"\n#include "gbt_compact.hpp"\n#include "kenma_model.hpp"\nnamespace hb1 {\ninline constexpr char const* dirc_feats[] = {\n'''+names+'''\n};\ninline constexpr int dirc_classes[] = {0,1,2};\ninline constexpr float dirc_base[] = {0,0,0};\ninline Model const dirc_bind{"kenma_a1_f0",270,dirc_feats,3,3,dirc_classes,dirc_base,0,nullptr,nullptr};\ninline std::vector<double> dirc_proba(std::vector<float> const& x) {\n    double p[4];\n    GBT_PROBA(kenma_model,x.data(),p);\n    double z=p[0]+p[1]+p[3];\n    return {p[0]/z,p[1]/z,p[3]/z};\n}\n}\n''')
meta=dict(source='Hinata A1-u fold f0; 400 of 800 iterations; development model, no refit',source_sha256=expected,features=features,export=info)
(out/'provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
(dst/'README.md').write_text('''# Kenma 02 — top-team direction prior\n\nParent: carthage-05-free-sprint at ea8ada4e2. Replaces only the direction prior with Hinata A1-u fold-f0, truncated to 400 boosting iterations. The top-ten pooled development model uses the same 270 HB-1 features; F/R/L are renormalised. Split, sprint, sonar and search remain the parent policy.\n\nThis is a development fold model, not a full-data fit. Model archive SHA-256: '''+expected+'''. Recreate with tools/kenma/prepare_a1.py; lane output build/kenma/a1/provenance.json records feature ordering and exporter counts.\n\nStatus: unmeasured. Native comparison, exported prediction parity, size and sandbox points are required.\n''')
with zipfile.ZipFile(out/'kenma-02-topteam-prior.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(dst.iterdir()):
        if p.suffix in ('.cpp','.hpp') or p.name=='bot.toml':
            z.write(p,p.name)
print(json.dumps(dict(export=info,zip_bytes=(out/'kenma-02-topteam-prior.zip').stat().st_size)),flush=True)
