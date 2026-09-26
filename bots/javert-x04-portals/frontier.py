"""Swarm-relative waypoints from the gradient of shared density evidence.

b=(enemies-allies)/(allies+enemies+1) increases toward enemy control.
Advance approaches the slightly allied b=-0.15 band; withdraw moves down the
balance gradient toward allied support. Compass samples estimate a derivative;
no spawn/team/compass constant selects the strategic direction.
"""
import math
import world as w
import roles
import density
from intentions import candidate


def balance(allies, enemies):
    return (enemies-allies)/(allies+enemies+1.0)


def orientation_supported():
    """A single footprint, uniform ratios, or age alone cannot create a front."""
    samples=[(x,y,balance(a,e)) for x,y,a,e,d in density.ACTIVE if d>=0.25 and a+e>=1.0]
    if len(samples)<2:return False
    low=min(samples,key=lambda s:s[2]);high=max(samples,key=lambda s:s[2])
    if high[2]-low[2]<0.15:return False
    return abs(density.delta(low[0],high[0],w.W))+abs(density.delta(low[1],high[1],w.H))>=2.0


def offset(dx,dy):
    return ((w.HEAD//w.W+dy)%w.H)*w.W+(w.HEAD%w.W+dx)%w.W


def build(ctx, mode):
    diagnostic=dict(reason='disabled',sources=len(density.ACTIVE),samples=0)
    if not mode:return [],diagnostic
    if not orientation_supported():
        diagnostic['reason']='no_supported_orientation';return [],diagnostic
    a0,e0,c0=density.field(w.HEAD);b0=balance(a0,e0)
    diagnostic.update(reason='no_improving_waypoint',balance=b0,confidence=c0)
    if c0<0.25:
        diagnostic['reason']='unknown_here';return [],diagnostic
    # Five shared field samples. Both sides of a derivative need evidence.
    samples=[density.field(offset(dx,dy)) for dx,dy in ((2,0),(-2,0),(0,2),(0,-2))]
    diagnostic['samples']=5
    if min(s[2] for s in samples)<0.2:
        diagnostic['reason']='unsupported_derivative';return [],diagnostic
    east,west,south,north=[balance(a,e) for a,e,_ in samples]
    gx=(east-west)/4.0;gy=(south-north)/4.0
    norm=math.sqrt(gx*gx+gy*gy)
    diagnostic['gradient']=(gx,gy)
    if norm<0.025:
        diagnostic['reason']='flat_field';return [],diagnostic
    out=[]
    for name in ('advance','withdraw'):
        if name=='advance':
            if mode!=1 or roles.ROLE[0]!='forager' or w.LEN>5 or w.UNITS<3:continue
            if abs(b0+0.15)<0.06:continue
            sign=1.0 if b0 < -0.15 else -1.0
            distances=[sign*k for k in (2,3,4,5)]
        else:
            if e0<0.3 or b0<=-0.45:continue
            distances=[-4.0]
        best=None
        for distance in distances:
            dx=int(round(distance*gx/norm));dy=int(round(distance*gy/norm))
            if abs(dx)+abs(dy)<2:continue
            cell=offset(dx,dy);steps=ctx['dist'].get(cell)
            if steps is None or not 2<=steps<=10:continue
            aa,ee,confidence=density.field(cell);diagnostic['samples']+=1
            if confidence<0.3 or aa<1.0:continue
            b=balance(aa,ee)
            if name=='advance':
                gain=abs(b0+0.15)-abs(b+0.15)
                if ee<0.25 or b>0.2 or gain<=0.04:continue
                kind='SCOUT'
            else:
                gain=b0-b+0.1*(aa-a0)
                if gain<=0.04 or b>=b0:continue
                kind='RETREAT'
            value=gain*confidence
            if best is None or value>best[0]:best=(value,cell,aa,ee,confidence,kind)
        if best is None:continue
        gain,cell,aa,ee,confidence,kind=best
        c=candidate(kind,cell,macro=name,macro_gain=gain,balance=b0,
                    allies=aa,enemies=ee,confidence=confidence,
                    protect=1.5 if roles.ROLE[0]=='crown' or w.LEN>=8 else 0,
                    emergency_split=True)
        c['candidate_id']=kind+':'+name+':'+str(cell)
        out.append(c)
    if out:diagnostic['reason']='available'
    diagnostic['waypoints']=[(c['params']['macro'],c['target']) for c in out]
    return out,diagnostic
