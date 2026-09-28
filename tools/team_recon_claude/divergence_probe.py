"""Single-block perturbation probe: rebuild dragon DID's blocks up to round R, replay its history into a fresh
bot process, then print the bot's first command for the base block and for message/echo/countdown variants.

    python3 divergence_probe.py REPLAY DID R BOTDIR
"""
import sys, subprocess
from pathlib import Path; sys.path.insert(0,str(Path(__file__).resolve().parent)); import recon, roundblock
rep, did, R, BOT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
g = recon.Game(rep); hist=[]; st={'n':0}
def cb(kind, **k):
    if kind=='turn' and k['dragon'].id==did:
        d=k['dragon']; p3=(st['n']>0 or d.parent is not None); st['n']+=1
        hist.append((g.round, roundblock.build_block(g,d,proto3=p3)))
        if g.round>=R: raise StopIteration
try: g.run(cb)
except StopIteration: pass
d=g.dragons[did]
def run(last):
    p=subprocess.Popen([sys.executable,'-u','main.py'],cwd=BOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
    s=f'ID {d.id}\nTEAM {d.team}\nMAP {g.board.W} {g.board.H}\nUNIT_LIMIT {g.board.unit_limit}\n'
    for r,b in hist[:-1]: s+='\n'.join(b)+'\n\n'
    s+='\n'.join(last)+'\n\nENDGAME\n'
    out=p.communicate(s)[0].split('ENDTURN')
    return out[-2].strip().splitlines()[0]
last=hist[-1][1]
print('\n'.join(last))
print('BASE', run(last))
import re
# variants
def sub(f):
    return [f(l) for l in last]
print('cd -1->0', run(sub(lambda l: re.sub(r' -1$',' 0',l) if len(l.split())==4 else l)))
print('no msgs', run([l for l in last if not l.isdigit()] and [('NUM_MSGS 0' if l.startswith('NUM_MSGS') else l) for l in last if not (l.isdigit())]))
print('echo0', run([('ECHOES 0 0 0 0 0' if l.startswith('ECHOES') else l) for l in last]))
i=[k for k,l in enumerate(last) if l.startswith('NUM_MSGS')][0]
for keep in ([0],[1]):
    ms=[last[i+1+j] for j in keep]
    print('keep',keep, run(last[:i]+['NUM_MSGS %d'%len(ms)]+ms+last[i+3:]))
g2=recon.Game(rep); log=[]
def cb2(kind,**k):
    if kind=='sonar' and k['hit']==did and g2.round>=R-2 and g2.round<=R: log.append((g2.round,k['sender'],k['direction'],k['hitkind'],k['origin'],k['end'],k['value64']))
    if kind=='turn' and g2.round>R: raise StopIteration
try: g2.run(cb2)
except StopIteration: pass
for x in log: print(x)
print('rev', run(last[:i]+['NUM_MSGS 2',last[i+2],last[i+1]]+last[i+3:]))
