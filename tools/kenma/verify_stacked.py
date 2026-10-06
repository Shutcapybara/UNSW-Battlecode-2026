"""End-to-end combined feature binding and exported prediction check on replay observations."""
from pathlib import Path
import collections,json,subprocess,sys
import numpy as np
import lightgbm as lgb
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT/'tools/learn'))
import rebuild,block,encode,labels,hb1prior
out=MAIN/'build/kenma/stacked-prior'
bot=ROOT/'bots/kenma-17-stacked-direction-prior'
(out/'runtime_check.cpp').write_text(r'''#include <fstream>
#include <iostream>
#include <string>
#include "policy.hpp"
#include "kenma_stacked.hpp"
int main(int argc,char** argv) {
    if(argc!=3)return 2;
    std::ofstream xf(argv[1],std::ios::binary),pf(argv[2],std::ios::binary);
    while(std::cin>>std::ws && std::cin.peek()!=EOF) {
        auto [ct,g]=unswbc::init();
        hb1::Proc hp(ct.get_id(),ct.get_team().value,g.width,g.height,g.unit_limit);
        kenma::Stacked slot(ct,g);
        while(unswbc::update(ct,g)) {
            auto row=hp.features(hb1::block_from(ct,g));slot.observe(ct,g,&row);
            xf.write(reinterpret_cast<char const*>(slot.x.data()),slot.x.size()*sizeof(float));
            pf.write(reinterpret_cast<char const*>(slot.p.data()),slot.p.size()*sizeof(double));
            std::string label,kind,value;std::cin>>label>>kind>>value;
            if(label!="ACT")return 3;
            if(kind=="m") {
                slot.act(1,int(std::string("FRBL").find(value[0])),int(value.size()),g.get_round_num());
                hp.record_move(value);
            } else if(kind=="s") {
                slot.act(2,-1,0,g.get_round_num());hp.record_split(std::stoi(value));
            } else slot.act(kind=="n" ? 3:0,-1,0,g.get_round_num());
        }
    }
}
''')
for src,dst,inc in [(out/'runtime_check.cpp',out/'runtime_check',bot),(ROOT/'tools/learn/cpp/hb1_feats.cpp',out/'parent_hb_feats',ROOT/'bots/carthage-05-free-sprint')]:
    subprocess.run(['clang++','-O2','-std=c++20','-Wno-overlength-strings','-I'+str(inc),str(src),'-o',str(dst)],check=True)
seqs=[];protocol=[];expected_enc=[];keys=[]
for path in sorted((MAIN/'build/kenma/k12-orbit-smoke').glob('*.replay')):
    kept={0,1};turns=collections.defaultdict(list)
    def emit(i,sp,txt,ctx):
        if i not in kept and len(kept)<10 and ctx['born']>0:kept.add(i)
        if i in kept and len(turns[i])<128:turns[i].append((sp,txt,ctx))
    rebuild.walk(path.read_bytes(),emit)
    for ident,ts in sorted(turns.items()):
        sp=ts[0][0];spawn=hb1prior.spawn_text(sp);protocol.append(spawn)
        enc=encode.Encoder(block.Spawn(sp['id'],sp['team'],sp['W'],sp['H'],sp['unit_limit']))
        hbturns=[]
        for sp,txt,ctx in ts:
            b=block.parse_block(txt);y=labels.label(ctx,b,ident,sp['team'])
            expected_enc.append(enc.observe(b));keys.append([path.name,ident,ctx['round']])
            hbturns.append((txt,y));protocol.append(txt)
            if y['y_kind']==0:
                protocol.append(f"ACT m {y['y_seq']}\n");enc.act('move',list(y['y_seq']))
            elif y['y_kind']==1:
                protocol.append(f"ACT s {y['y_child']}\n");enc.act('split',child=y['y_child'],rnd=ctx['round'])
            else:
                protocol.append('ACT n 0\n' if y['y_kind']==2 else 'ACT t 0\n');enc.act('invalid' if y['y_kind']==2 else 'none')
        protocol.append('ENDGAME\n');seqs.append((spawn,hbturns))
print('prepared',len(keys),'turns from',len(seqs),'processes',flush=True)
p=subprocess.run([str(out/'parent_hb_feats')],input=hb1prior.fixture(seqs),capture_output=True,text=True,check=True)
lines=p.stdout.splitlines();names=lines[0].split()[2:]
hb=np.array([[float(v) for v in s.split()] for s in lines[1:]],dtype=np.float32)
features=(out/'features.txt').read_text().splitlines()
assert ['hb_f_'+n for n in names]==features[1193:1463]
expected=np.concatenate([np.array(expected_enc,dtype=np.float32),hb[:,3:],hb[:,:3]],axis=1)
assert expected.shape==(len(keys),1466)
subprocess.run([str(out/'runtime_check'),str(out/'runtime-features.f32'),str(out/'runtime-probabilities.f64')],input=''.join(protocol),text=True,check=True)
actual=np.fromfile(out/'runtime-features.f32',dtype=np.float32).reshape(-1,1466)
same=(expected==actual)|(np.isnan(expected)&np.isnan(actual))
if not same.all():
    bad=np.argwhere(~same);print('feature mismatches',[(keys[i],features[j],float(expected[i,j]),float(actual[i,j])) for i,j in bad[:12]],flush=True)
    raise SystemExit(1)
model=lgb.Booster(model_file=str(out/'A5-400-f0.txt'))
ref=model.predict(expected,num_threads=1)
pred=np.fromfile(out/'runtime-probabilities.f64',dtype=np.float64).reshape(-1,4)
error=float(np.max(np.abs(ref-pred)));assert error<1e-6
assert np.array_equal(ref.argmax(1),pred.argmax(1))
report={'turns':len(keys),'processes':len(seqs),'replays':4,'exact_feature_values':int(expected.size),'features':1466,'prediction_argmax_agreement':len(keys),'max_probability_error':error,'source':'first128 turns of both original queens and eight born-later dragons per retained smoke replay','note':'Compares helper/runtime encoder against Python encoder and canonical parent HB exporter; same recorded observations/actions, not a counterfactual game-strength result.'}
(out/'runtime-parity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
