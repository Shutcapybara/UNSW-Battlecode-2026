"""Vicious: bounded phase policy and per-dragon intent. All switches default off.

Only local observations and checked sonar packets enter this module. No map or
opponent names. R is the configured rules horizon (not observed game duration).
"""
import world as w
import roles
import tactics as tx
import comms
from params import P

STATE = {'phase': 'opening', 'open': 0.0, 'late': 0.0, 'age': 0,
         'intent': None, 'pressure': 0.0, 'food': 0, 'changed': 0}
BEDS = {}
PERIOD = {}
BASE = {k: P[k] for k in ('split_stop', 'grow_from')}


def schedule(r, horizon=500, opening=60, conversion=360, mode='hard', width=60):
    """Global zero-based round, independent of process birth/dragon age."""
    assert 0 <= opening < conversion < horizon
    phase = 'opening' if r < opening else 'middle' if r < conversion else 'endgame'
    if mode == 'static': return phase, 1.0, 1.0
    if mode == 'soft':
        return phase, max(0.0, min(1.0, (opening-r)/max(1,width))), max(0.0,min(1.0,(r-conversion)/max(1,width)))
    return phase, float(r < opening), float(r >= conversion)


def degree(cell):
    # Unknown edges are not proof of a junction or a dead end.
    ds=w.dest(cell)
    return sum(n >= 0 for n in ds), any(n in (-2,-3) for n in ds)


def corridor_goal(head, occupied):
    """Walk a known single-exit passage until a junction, bounded at 8 tiles."""
    choices=[n for n in w.dest(head) if n >= 0 and n not in occupied and n not in w.occ]
    if len(choices) != 1: return None
    prev, cur = head, choices[0]
    seen={head}
    for _ in range(8):
        seen.add(cur)
        ds=w.dest(cur)
        if any(n in (-2,-3) for n in ds):return cur
        onward=[n for n in ds if n >= 0 and n != prev and n not in occupied and n not in seen]
        if len(onward) != 1:return cur if onward else None
        prev,cur=cur,onward[0]
    return cur


def observe():
    enabled=any(P.get(k,0) for k in ('temporal_egress','temporal_split_guard','temporal_open_bonus','temporal_conversion','temporal_crown_state'))
    if not enabled:return
    r=w.RND
    phase,op,late=schedule(r,P.get('temporal_horizon',500),P.get('temporal_open_until',60),P.get('temporal_convert_from',360),P.get('temporal_mode','hard'),P.get('temporal_ramp',60))
    STATE.update(phase=phase,open=op,late=late,age=r-w.BORN,
                 progress=r/P.get('temporal_horizon',500),remaining=P.get('temporal_horizon',500)-r,
                 pressure=len(w.enemy_heads),food=sum(v==r for v in w.pearls.values()),changed=0)
    # Direct repeated countdowns identify regeneration; gossip never sets period.
    if P.get('temporal_open_bonus',0):
        for x,y,pearl,cd in w.io_tiles():
            c=y*w.W+x
            if cd < 0:continue
            due=r+cd
            old=BEDS.get(c)
            if old is not None and due > old and 1 <= due-old <= 50:PERIOD[c]=due-old
            BEDS[c]=due
    if P.get('temporal_egress',0):
        intent=STATE['intent']
        if intent and (r > intent[1] or w.HEAD == intent[0]):STATE['intent']=None
        if r == w.BORN and r < P.get('temporal_egress_until',500) and STATE['intent'] is None:
            deg,unknown=degree(w.HEAD)
            if deg <= 2 and not unknown:
                goal=corridor_goal(w.HEAD,set(w.body))
                if goal is not None:STATE['intent']=(goal,r+P.get('temporal_intent_ttl',8),'local')
    if P.get('temporal_crown_state',0):
        # A small elected dragon remains a collector until it can carry mass.
        if roles.ROLE[0]=='crown' and w.LEN < P.get('temporal_carrier_min',8) and w.RND < BASE['split_stop']:
            roles.ROLE[0]='forager'
            if w.crown is not None and w.crown[0]==(w.ME&4095):w.crown=None
    if P.get('temporal_conversion',0):convert()


def resource_value(cell,value):
    bonus=P.get('temporal_open_bonus',0)
    if not bonus or not STATE['open']:return value
    fast=PERIOD.get(cell,99) <= P.get('temporal_fast_period',25)
    # Crowded or contested renewable income supports collectors. Exploration
    # and one-off corpse pearls are not mislabeled as renewable production.
    useful=fast and (len(w.ally_heads) >= len(w.enemy_heads) or not w.enemy_heads)
    if P.get('temporal_condition','joint') == 'time':useful=True
    return value*(1+bonus*STATE['open']) if useful else value


def convert():
    c=w.crown
    STATE['receiver']=False
    P['split_stop']=BASE['split_stop'];P['grow_from']=BASE['grow_from']
    r=w.RND
    time_gate=STATE['late'] > 0
    # Keep collectors and avoid a stale crown causing an irreversible phase.
    receiver=c is not None and c[0] != (w.ME&4095) and 0 <= r-c[3] <= 4 and c[2] >= max(8,2*w.LEN)
    state_gate=receiver and w.UNITS >= 6 and len(w.enemy_heads) <= len(w.ally_heads)+1
    cond=P.get('temporal_condition','joint')
    gate=state_gate if cond == 'state' else time_gate if cond == 'time' else time_gate and state_gate
    if not gate:return
    STATE['receiver']=bool(receiver)
    # A fractional schedule staggers cohorts deterministically; emergency
    # splits remain in the inherited fallback and the crown may be rescued.
    weight=1.0 if cond == 'state' else STATE['late']
    cohort=((w.ME*17)%16)/16
    if cohort >= 0.75*weight:return  # retain at least 25% collectors
    if receiver and w.LEN <= P.get('temporal_donor_max',8):
        distance=w.tdist(w.HEAD,c[1])
        if distance <= min(36, P.get('temporal_horizon',500)-r-12):
            roles.ROLE[0]='feeder'
            P['split_stop']=min(BASE['split_stop'],r)
            P['grow_from']=min(BASE['grow_from'],r)


def donation_allowed(ch):
    if not P.get('temporal_conversion',0):return True
    c=w.crown
    if c is None or c[2] < max(8,2*w.LEN) or w.LEN > P.get('temporal_donor_max',8):return False
    if w.UNITS < 4 or w.RND < P.get('temporal_donate_from',400):return False
    if any(w.tdist(ec,ch)<=2 for ec,_ in w.enemy_heads):return False
    # Certify a short terrain route instead of donating through nearby walls.
    q=[ch];ds={ch:0}
    own=set(w.body)
    while q and len(ds) <= 24:
        cur=q.pop(0)
        if cur in own:return True
        if ds[cur] >= 3:continue
        for n in w.dest(cur):
            if n < 0 or n in ds:continue
            o=w.occ.get(n)
            if o is not None and n != ch:continue
            if any(w.tdist(ec,n) <= ds[cur]+1 for ec,_ in w.enemy_heads):continue
            ds[n]=ds[cur]+1;q.append(n)
    return False


def adjust(ranked,threat):
    eg=P.get('temporal_egress',0);guard=P.get('temporal_split_guard',0)
    if not eg and not guard:return ranked
    original=max(ranked,key=lambda p:p[0])[1]
    intent=STATE['intent']
    distances={}
    if eg and intent:
        # Route through known geometry, never a torus-vector pull through walls.
        goal=intent[0];q=[w.HEAD];distances={w.HEAD:0};first={w.HEAD:None}
        i=0
        while i<len(q) and len(q)<32:
            c=q[i];i+=1
            for d,n in enumerate(w.dest(c)):
                if n < 0 or n in distances or n in w.occ or n in w.body:continue
                distances[n]=distances[c]+1;first[n]=d if c==w.HEAD else first[c];q.append(n)
        direction=first.get(goal)
    else:direction=None
    out=[]
    for score,act in ranked:
        kind,arg=act;delta=0.0
        if kind=='move' and direction is not None and arg[0]==direction and score > -900:
            if tx.sim(arg,w.body)[0]=='ok':delta=P.get('temporal_intent_bonus',3.0)
        if kind=='split' and guard and score > -500 and len(w.body)==w.LEN:
            # After splitting, BOTH halves still occupy their original cells.
            # Inherited flood simulates each separately and can credit space
            # through the other half. Admit only a two-step newborn route.
            child=w.body[:arg][::-1];blocked=set(w.body)|set(w.occ)
            exits=[n for n in w.dest(child[-1]) if n >= 0 and n not in blocked]
            viable=any(any(z >= 0 and z not in blocked and z != child[-1]
                           for z in w.dest(n)) for n in exits)
            if not viable:delta=-40.0
        out.append((score+delta,act))
    STATE['changed']=int(max(out,key=lambda p:p[0])[1] != original)
    STATE['parent_choice']=original
    return out


def send(work):
    if not P.get('temporal_egress',0) or w.RND >= P.get('temporal_egress_until',500) or work['selected'][0] != 'split':return
    n=work['selected'][1]
    if len(w.body) != w.LEN or w.NC > 4096 or n > 255:return
    childhead=w.body[0]
    goal=corridor_goal(childhead,set(w.body))
    if goal is None:return
    # Target by birth cell, round and exact child size; no unaddressed command
    # can change an older nearby dragon. The rear ray refracts through parent.
    p=childhead | (goal<<12) | (w.RND<<24) | (n<<33)
    work['messages'][w.DIRS[(w.FACE+2)%4]]=comms.pack(7,p)


def hear(p):
    birth=p&4095;goal=(p>>12)&4095;r=(p>>24)&511;ln=(p>>33)&255
    if w.RND==w.BORN==r and birth==w.HEAD and ln==w.LEN and goal<w.NC:
        STATE['intent']=(goal,r+P.get('temporal_intent_ttl',8),'parent')


def trace(work):
    if not P.get('temporal_trace',0):return
    if STATE.get('changed') or STATE.get('intent') or roles.ROLE[0]=='feeder' or w.RND%50==0:
        print('LOG VIC',w.RND,w.ME,STATE['phase'],roles.ROLE[0],STATE['changed'],STATE.get('intent'),work['selected'],STATE.get('parent_choice'))


def before_roles():
    """Refresh length from direct observations before election, not only position.

    A complete chain proves current length; a cut chain is only a lower bound.
    Receiving a fresh position must not renew an obsolete pre-split length.
    """
    if not P.get('temporal_crown_state',0):return
    c=w.crown
    if c is None or c[0]==(w.ME&4095):return
    for cell,did in w.ally_heads:
        if (did&4095)==c[0]:
            visible=w.alen.get(did,1)
            portal_cut=any(any(w.ek[w.ekey(cell,d)]==3 for d in range(4))
                           for cell,o in w.occ.items() if o[0]==did)
            if visible >= 2 and did not in w.cut and not portal_cut:c[2]=visible
            else:c[2]=max(c[2],visible)
            c[1]=cell;c[3]=w.RND
            break
