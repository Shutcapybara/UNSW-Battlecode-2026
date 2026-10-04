"""Action labeller (Data lane, kageyama). One label row per dragon turn, from the replay-side ctx that rebuild.walk
emits (labels only; never encoder input). LABEL_VERSION 1.

Conventions (HB-1 compatible where HB-1 has the field):
  y_kind      0 move, 1 split, 2 invalid/suicide (engine 'suicide' = the command could not be applied), 3 no action (tle)
  y_first     first step relative to the facing at turn start: 0 F, 1 R, 2 B, 3 L; -1 when not a move
  y_nsteps    steps sent (1 = walk, >1 = sprint); y_seq the relative sequence, each step relative to the previous one
  y_child     split child size (the SPLIT argument); y_parent = length - child
  y_sonar_mask  requested sonar directions relative to the turn-start facing, bits F=1 R=2 B=4 L=8 (HB-1). A ray
              that left through the tail (origin != head after the action) was aimed into the neck: requested = B of
              the post-action facing, re-expressed relative to the turn-start facing
  y_sonar_mask_phys  the same over the physical (recorded) ray directions - HB-1's convention, which loses the
              requested bit of a refracted ray; kept for the HB-1 agreement check only
  y_sonar_n   rays cast; y_sonar_v64 rays with a payload > 2^32; y_sonar_v0 rays with payload 0
  y_died      the dragon died during its own turn; y_death cause (wall/self/body/h2h/invalid)
  y_cull      deliberate cull: y_kind == 2 (invalid command), or a death by self-collision with an ally part adjacent to
              the head at turn start (read from the block, i.e. visible to the dragon)
"""
DIRS = 'NESW'
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
LABEL_VERSION = 1
COLS = ['y_kind', 'y_first', 'y_nsteps', 'y_seq', 'y_child', 'y_parent', 'y_sonar_mask', 'y_sonar_mask_phys', 'y_sonar_n', 'y_sonar_v64',
        'y_sonar_v0', 'y_died', 'y_death', 'y_cull']


def rel(a, base):
    return (DIRS.index(a) - DIRS.index(base)) % 4


def label(ctx, blk=None, my_id=None, my_team=None):
    a, fac = ctx['action'], ctx['facing']
    y = dict(y_kind=3, y_first=-1, y_nsteps=0, y_seq='', y_child=0, y_parent=0)
    if a is not None and not ctx['tle']:
        if a[0] == 'move':
            rels, c = [], fac
            for s in a[1]:
                rels.append('FRBL'[rel(s, c)]); c = s
            y.update(y_kind=0, y_first='FRBL'.index(rels[0]) if rels else -1, y_nsteps=len(rels), y_seq=''.join(rels))
            if not rels:
                y['y_kind'] = 2
        elif a[0] == 'split':
            y.update(y_kind=1, y_child=a[1], y_parent=ctx['length'] - a[1])
        else:
            y['y_kind'] = 2
    mask = n = v64 = v0 = phys = 0
    for p in ctx['sonar']:
        phys |= 1 << rel(p['dir'], fac)
        d = p['dir'] if p['origin'] == ctx['head_after'] else OPP[ctx['facing_after']]
        mask |= 1 << rel(d, fac)
        n += 1
        v64 += p['value'] > 0xFFFFFFFF
        v0 += p['value'] == 0
    y.update(y_sonar_mask=mask, y_sonar_mask_phys=phys, y_sonar_n=n, y_sonar_v64=v64, y_sonar_v0=v0)
    death = ctx['death']
    y['y_died'] = int(death is not None)
    y['y_death'] = death or ''
    cull = y['y_kind'] == 2 or death == 'invalid'
    if not cull and death == 'self' and blk is not None:
        hx, hy = blk.tiles[24][0], blk.tiles[24][1]
        near = {(blk.tiles[k][0], blk.tiles[k][1]) for k in (17, 23, 25, 31)}
        cull = any(t == my_team and i != my_id and (x, y_) in near for t, i, x, y_, f, h in blk.parts)
    y['y_cull'] = int(cull)
    return y
