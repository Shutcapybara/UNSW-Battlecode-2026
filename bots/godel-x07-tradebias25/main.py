"""ouroboros-v13-ladder: v12-core with the compact-map ladder doctrine on.

One process per dragon.  Each turn:

    SENSE    world.py     parse the wire -> persistent world model
    LISTEN   comms.py     fold sonar gossip into the model
    ROLE     roles.py     crown election, feeding, production doctrine
    TARGET   targets.py   role-weighted goal field
    SEARCH   evaluate.py  candidates (moves, sprints, strikes, splits, dives)
    FILTER   safety.py    exact simulation, threat, space and trap tests
    EVALUATE evaluate.py  one evaluation function in length units -> argmax
    ACT      main.py      emit the action, then the 4 sonar rays (comms.py)

Tunables: defaults.py (P, RP); overrides: params.py (PARAMS = {...}).

The modules share ONE global namespace: main.py exec()s them in order into
its own globals.  Hot functions keep plain global lookups (the same speed as
the single-file v10), and each file can be read and edited on its own.
"""
import gc
import os
import sys

gc.disable()  # no reference cycles worth collecting; GC pauses cost judge points

HERE = os.path.dirname(os.path.abspath(__file__))

MODULES = ("defaults", "world", "comms", "safety", "targets", "roles", "evaluate", "ladder")


def _load(name):
    """Source when present (local runs); else the judge's bytecode: the judge
    compiles every *.py to a legacy *.pyc beside it and deletes the source."""
    path = os.path.join(HERE, name + ".py")
    if os.path.exists(path):
        with open(path) as fh:
            return compile(fh.read(), path, "exec")
    import marshal
    with open(path + "c", "rb") as fh:
        return marshal.loads(fh.read()[16:])


for _m in MODULES:
    exec(_load(_m), globals())
del _m


# ======================================================================
# ACT
# ======================================================================
def commit_path(path):
    global MOVED_DIR
    MOVED_DIR = path[-1]
    cell = HEAD
    for d in path:
        n = dest(cell)[d]
        if n < 0:
            break
        cell = n
        trail.append(cell)
    emit("MOVE " + "".join(DIRS[d] for d in path))


def boot_turn(mine):
    """First turn of a new process: interpreter boot ate most of the budget.
    Take the safest single step."""
    body = body_list()
    best = -1
    bv = -1e9
    for d in range(4):
        res = simulate([d], body)
        if not res[0]:
            continue
        c = res[1]
        v = 0.0
        for m in dest(c):
            o = occ.get(m)
            if o is not None:
                if o[2] and not o[1]:
                    v -= 5.0
                elif o[2]:
                    v -= 2.0
                else:
                    v -= 0.5
            elif m < 0:
                v -= 0.3
        if c in pearls:
            v += 1.0
        if handoff is not None and handoff[1] >= 0:
            v -= 0.05 * tdist(c, handoff[1])
        if v > bv:
            bv = v
            best = d
    if best < 0:
        best = fallback_move()
        trail.append(dest(HEAD)[best] if dest(HEAD)[best] >= 0 else HEAD)
        emit("MOVE " + DIRS[best])
    else:
        commit_path([best])
    send_sonars()


def take_turn():
    global ROLE
    visits[HEAD] = min(255, visits[HEAD] + 1)
    broadcast_sightings()
    if RND % 16 == 0:
        prune()
    if update_role():
        return  # feeding: no action, the engine's default is to die here
    got = ladder_decide() if ladder_active() else None
    if got is None:
        got = decide()
    if got is None:
        d = fallback_move()
        if TRACE:
            trace("r%d FALLBACK d%d head%d body%s dest%s occ%s" % (RND, d, HEAD, body_list(), dest(HEAD), [occ.get(n) for n in dest(HEAD)]))
        n = dest(HEAD)[d]
        trail.append(n if n >= 0 else HEAD)
        emit("MOVE " + DIRS[d])
        send_sonars()
        return
    (v, act, kind), target = got
    if kind == "split":
        n = act
        role = child_role()
        if ROLE == CROWN and n > LEN - n:
            # an emergency split sheds most of the crown into the newborn:
            # the newborn is the crown now
            role = CROWN
            ROLE = GATHER
        emit("SPLIT %d" % n)
        # the child's head is our old tail; a ray fired back into our own
        # body exits at the (new) tail and lands on the child's head
        back = neck_dir()
        msg = handoff_packet(role, target)
        # body after split
        del trail[:-(LEN - n)]
        send_sonars(back, msg)
        return
    commit_path(act)
    send_sonars()


# ======================================================================
# MAIN
# ======================================================================
def main():
    global W, H, MY_ID, TEAM, UNIT_LIMIT, RND, LEN, UNITS, FACING, echo, ROLE, BORN, SALT
    p = parts()
    if not p:
        return
    MY_ID = int(p[1])
    TEAM = parts()[1]
    p = parts()
    W = int(p[1])
    H = int(p[2])
    UNIT_LIMIT = int(parts()[1])
    SALT = 0x5A if TEAM == "A" else 0xC3
    setup()
    first = True
    while True:
        p = parts()
        if not p or p[0] == "ENDGAME":
            return
        RND = int(p[1])
        FACING = DIRS.index(parts()[1][0])
        LEN = int(parts()[1])
        UNITS = int(parts()[1])
        nmsg = int(parts()[1])
        msgs = [int(parts()[0]) for _ in range(nmsg)]
        f = parts()
        echo = (0, 0, 0, 0, 0)
        if f[0] == "ECHOES":
            echo = tuple(int(v) for v in f[1:6])
            f = parts()
        tiles = [f] + [parts() for _ in range(48)]
        nb = int(parts()[1])
        bodies = [parts() for _ in range(nb)]
        rows_h = [parts() for _ in range(8)]
        rows_v = [parts() for _ in range(7)]
        if TRACE:
            import time
            t0 = time.perf_counter()
        if first:
            BORN = RND
        for m in msgs:
            hear(m)
        mine = sense(tiles, bodies, rows_h, rows_v)
        if first:
            seed_trail(mine)
            if RND == 0:
                ROLE = GATHER
            elif handoff is not None:
                ROLE = handoff[0]
            elif P["orphan_role"]:
                ROLE = orphan_role()
            else:
                ROLE = HUNT if LEN <= 2 else GATHER
        if trail and trail[-1] != HEAD:
            trail.append(HEAD)
        if len(trail) > 400:
            del trail[:-300]
        if first and RND > 0:
            boot_turn(mine)
        else:
            take_turn()
        if TRACE:
            trace("T r%d len%d dt=%.2fms n_enemy=%d occ=%d" % (RND, LEN, (time.perf_counter() - t0) * 1000, len(enemy_heads), len(occ)))
        first = False
        flush()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        if TRACE:
            import traceback
            trace("CRASH\n" + traceback.format_exc())
        raise
