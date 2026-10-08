"""Official-engine request delivery to a distant donor and native feed response.

Run with .venv/bin/python tests/test_kuroo_distress_delivery.py.
"""
from pathlib import Path
import json,os,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools/learn'))
import block
from tools.analysis.features.frame import decode
try:
 from unswbc.engine import EngineModule
except ImportError:
 EngineModule=None

@unittest.skipIf(EngineModule is None,'requires official engine in .venv')
class DistressDeliveryTest(unittest.TestCase):
 def test_native_donor_and_queen_food(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);exe=p/'bot'
   subprocess.run(['g++','-std=c++20','-O2',str(ROOT/'bots'/os.environ.get('KUROO_DISTRESS_BOT','kuroo-06-targeted-distress')/'main.cpp'),'-o',str(exe)],check=True)
   lines=(ROOT/'maps/live/default_small.map').read_text().splitlines();lines=lines[:lines.index('DRAGON_COUNT 4')]
   lines=[('EDGE '+l.split()[1]+' 0 -1') if l.startswith('EDGE ') else ('TILE '+' '.join(l.split()[1:3])+' 0 0') if l.startswith('TILE ') else l for l in lines]
   queen=[(5,4),(5,3),(5,2),(5,1),(5,0),(4,0),(3,0),(2,0)]
   donor=[(x,5) for x in range(12,-1,-1)]+[(x,6) for x in range(16)]+[(x,7) for x in range(15,7,-1)]
   assert len(donor)==37
   lines+=['DRAGON_COUNT 3']
   for team,body in [(0,queen),(1,[(14,11),(14,12),(14,13)]),(0,donor)]:
    lines.append(f'DRAGON {team} {len(body)} '+' '.join(f'{x} {y}' for x,y in body))
   text='\n'.join(lines+['END'])+'\n'
   payload=2|(7<<12)|(5<<19)|(436<<26)|(8<<36)
   low=0xd3|(8<<8)|(payload<<12);h=(low*0x9E3779B97F4A7C15)&((1<<64)-1)
   packet=low|(((h>>56)^((h>>17)&255))<<56)
   process=None;turns=[]
   def spawn(i,raw):
    nonlocal process
    if i==2:
     process=subprocess.Popen([str(exe)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
     process.stdin.write(raw.decode());process.stdin.flush()
   def reply(i,raw):
    b=block.parse_block(raw)
    if i==2:
     process.stdin.write(raw.decode().replace(f'ROUND {b.round}\n',f'ROUND {435+b.round}\n',1));process.stdin.flush();reply=[]
     while True:
      line=process.stdout.readline()
      if not line:raise RuntimeError('donor stopped')
      reply.append(line)
      if line.strip()=='ENDTURN':break
     out=''.join(reply);turns.append({'round':b.round,'msgs':b.msgs,'reply':out});return out.encode()
    if b.round>=3:return b'MOVE\nPROTOCOL 3\nENDTURN\n'
    move=('E' if b.round<2 else 'S') if i==0 else b.dir
    out=f'MOVE {move}\nPROTOCOL 3\n'
    if i==0 and b.round==1:out+=f'SONAR S {packet}\n'
    return (out+'ENDTURN\n').encode()
   e=EngineModule()
   try:
    e.run(text.encode(),reply,bot_spawn=spawn,debug=0,seed=81036)
    (p/'case.replay').write_bytes(e.replay('distress-A','fixture-B'))
   finally:
    if process:
     process.stdin.write('ENDGAME\n');process.stdin.flush();process.communicate(timeout=5)
   f=decode(p/'case.replay');event=next(t for t in turns if t['round']==1)
   self.assertIn(packet,event['msgs']);self.assertIn('LOG QD:F',event['reply'])
   self.assertTrue(any(d['id']==2 and d['round']==1 and d['cause']=='self' for d in f['events']['deaths']))
   self.assertEqual(len(f['rounds'][3][0][1]),9)
   print('same-round distant donor feed confirmed; queen grows8->9 on donated food')
if __name__=='__main__':unittest.main()
