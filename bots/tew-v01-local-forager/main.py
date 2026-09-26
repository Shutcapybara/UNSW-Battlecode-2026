"""Tew v01: local safe foraging with anti-dither memory."""
from enum import Enum, auto
import protocol as io

class Intent(Enum):
    MOVE = auto()
    SPLIT = auto()

state = {}
work = {}
DIRS = {"N": (0,-1), "E": (1,0), "S": (0,1), "W": (-1,0)}


def initialize_state():
    state.update(visits={}, last=None, stuck=0)

def decode_messages():
    pass

def update_state():
    ob = io.observation
    state['round'] = ob['round']
    tiles = {(x,y):(pearl, countdown) for x,y,pearl,countdown in ob['tiles']}
    # Center tile is tile 24; coordinates wrap on the torus.
    x,y = ob['tiles'][24][:2]
    W,H = io.game['size']
    state['pos']=(x,y); state['W']=W; state['H']=H
    occ={}
    for b in ob['bodies']:
        occ[(int(b[2]),int(b[3]))]=(b[0], int(b[1]), b[5]=='1')
    state['tiles']=tiles; state['occ']=occ

def build_actions():
    x,y=state['pos']; W,H=state['W'],state['H']; ob=io.observation
    # Close/collision checks use visible body geometry and the edge grids.
    edges={}
    for r,row in enumerate(ob['horizontal_edges']):
        for c,t in enumerate(row): edges[('h',c,r)]=t
    for r,row in enumerate(ob['vertical_edges']):
        for c,t in enumerate(row): edges[('v',c,r)]=t
    opts=[]
    for d,(dx,dy) in DIRS.items():
        nx,ny=(x+dx)%W,(y+dy)%H
        # A step is legal only when the corresponding edge is known open.
        if d=='N': edge=edges.get(('h',3,3))
        elif d=='S': edge=edges.get(('h',3,4))
        elif d=='W': edge=edges.get(('v',3,3))
        else: edge=edges.get(('v',4,3))
        if edge != '.': continue
        if (nx,ny) in state['occ']: continue
        pearl,cd=state['tiles'].get((nx,ny),(0,-1))
        if cd >= 0 and not pearl: continue
        # Prefer immediate growth, safe exits, and unexplored locations.
        exits=0
        for ex,ey in DIRS.values():
            ax,ay=(nx+ex)%W,(ny+ey)%H
            if (ax,ay) not in state['occ'] and state['tiles'].get((ax,ay),(0,-1))[1] < 0: exits+=1
        visits=state['visits'].get((nx,ny),0)
        score=(20 if pearl else 0) + min(exits,3)*1.3 - visits*1.1
        if state.get('last')==d: score+=0.15
        opts.append((score,d,nx,ny))
    work['actions']=opts

def choose_action():
    if work['actions']:
        work['selected']=max(work['actions'])
    else:
        work['selected']=None

def execute_action():
    sel=work['selected']
    if sel is None:
        # Normally impossible on a valid map; maintain valid transport.
        d=io.observation['direction']
    else:
        _,d,nx,ny=sel
        state['pos']=(nx,ny); state['visits'][(nx,ny)]=state['visits'].get((nx,ny),0)+1
        state['last']=d
    io.reply.update(command=io.Command.MOVE, argument=d)

def construct_messages(): pass
def encode_messages(): pass
def record_diagnostics(): pass

def main():
    if not io.read_init(): return
    initialize_state()
    while io.read_turn():
        work.clear(); work['actions']=[]; io.reply.clear(); io.reply['sonar']={}
        decode_messages(); update_state(); build_actions(); choose_action(); execute_action()
        construct_messages(); encode_messages(); record_diagnostics(); io.write_reply()

if __name__=='__main__': main()
