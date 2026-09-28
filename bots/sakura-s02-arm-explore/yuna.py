"""Yuna mechanisms: temporal portal policy, local donor chain, newborn exit,
momentum.  Each is gated by params (0 = host behaviour) and traced through
EVENTS (emitted as LOG lines when P['phase_trace'] is set)."""
import world as w
import tactics as tx
import roles
import phase
from params import P

EVENTS = []
EXPLORE_DIR = [-1]   # sakura s02: first direction that earned an exploration bonus this turn


def explore_rich():
    """sakura s02 (H-explore): the portal-dive bias applies only on maps with
    many portal pairs (counted from the atlas when it matched, else as learnt)."""
    return P["sk_explore"] and w.portal_pairs() >= P["sk_explore_pairs"]


def ev(tag):
    if P["phase_trace"]:
        EVENTS.append(tag)


# ---------------------------------------------------------------- portals
def enemy_near(cell):
    r = P["pb_enemy_r"]
    ttl = P["pb_enemy_ttl"]
    rnd = w.RND
    for c, t in w.eseen.items():
        if rnd - t <= ttl and w.tdist(c, cell) <= r:
            return True
    return False


def blind_risk():
    if not P["portal_mode"]:
        return P["p_blind"]
    pb = phase.by_phase("pb")
    if explore_rich():
        ph = phase.phase()
        if ph == "mid":
            pb = min(pb, P["pb_rich_mid"])
        elif ph == "end":
            pb = min(pb, P["pb_rich_end"])
    c = tx.BLINDC[0]
    if c is not None and c >= 0:
        pr = w.PRES.get(c)
        if pr is not None and w.RND - pr[0] <= P["probe_ttl"]:
            ev("probe_use")
            return pb * P["probe_clear_mult"] if pr[1] else max(pb, P["probe_block_pb"])
        hr = w.HOLD.get(c)
        if hr is not None and w.RND - hr <= P["hold_ttl"]:
            ev("hold_use")
            return max(pb, P["probe_block_pb"])
    if c >= 0 and w.seen[c] and w.RND - (w.seen[c] - 1) <= P["pb_fresh"] and not enemy_near(c):
        pb *= P["pb_safe_mult"]
    return pb


def vdive():
    if not P["portal_mode"]:
        return P["v_dive"]
    v = phase.by_phase("vdive")
    if explore_rich() and phase.phase() == "mid":
        v = max(v, P["vdive_rich_mid"])
    return v


def explore_bonus(d):
    if not P["portal_mode"] or w.LEN > P["explore_max_len"]:
        return 0.0
    eps = phase.by_phase("eps")
    if explore_rich() and phase.phase() == "mid":
        eps = max(eps, P["eps_rich_mid"])
    if eps <= 0:
        return 0.0
    for hc, hid in w.ally_heads:
        if w.tdist(hc, w.HEAD) <= 2 and hid < w.ME:
            eps *= 0.5   # a nearby (older) ally is the likelier explorer
            break
    if phase.rng(w.RND // 8, d, 7) < eps:
        ev("explore")
        EXPLORE_DIR[0] = d
        return P["v_explore"]
    return 0.0


# ---------------------------------------------------------------- donors
def donor_action(body):
    m = P["donor_mode"]
    if not m or roles.ROLE[0] == "crown":
        return None
    L = w.LEN
    if L > P["donor_max_len"]:
        return None
    if m in (1, 2):
        if phase.weight("dn") <= 0:
            return None
    elif m == 4:
        g = phase.weight("dn")
        if g <= 0 or phase.rng(w.RND, 11) >= g * P["donor_p"]:
            return None
    # receiver: a visible allied head clearly longer than us, close enough to collect
    best = None
    for hc, hid in w.ally_heads:
        if w.tdist(hc, w.HEAD) > P["donor_dist"]:
            continue
        al = w.alen.get(hid, 1)
        if al >= L + P["donor_margin"] and (best is None or al > best[1]):
            best = (hc, al)
    if best is None:
        return None
    if m in (2, 3):
        if w.UNITS < P["donor_min_units"]:
            return None
        for ec, _e in w.enemy_heads:
            if w.tdist(ec, w.HEAD) <= 3:
                return None   # the corpse would feed the enemy
    back = (w.FACE + 2) % 4
    for d in [back, 0, 1, 2, 3]:
        if tx.sim([d], body)[0] == "dead":
            ev("donate")
            return (0.0, ("move", [d]))
    return None


# ---------------------------------------------------------------- newborn exit
def note_birth():
    if w.RND != w.BORN or w.RND == 0:
        return
    best = -1
    bd = 99
    for hc, _hid in w.ally_heads:
        d = w.cheb(hc, w.HEAD)
        if d <= 3 and d < bd:
            bd = d
            best = hc
    w.PARENT[0] = best
    if best >= 0 and P["nb_mode"] == 2:
        # state gate: only a birth in a tight pocket needs the exit rule
        room = tx.flood(w.body, P["nb_tight"], 0)
        if room >= P["nb_tight"]:
            w.PARENT[0] = -1
        else:
            ev("nb_tight")


def newborn_active():
    return P["nb_mode"] and w.PARENT[0] >= 0 and w.RND - w.BORN <= P["nb_age"]


def newborn_blocks(c):
    return w.tdist(c, w.PARENT[0]) <= P["nb_radius"]


def newborn_push(h):
    p = w.PARENT[0]
    if w.tdist(h, p) < w.tdist(w.HEAD, p):
        return P["nb_push"]
    return 0.0


# ---------------------------------------------------------------- momentum
def mom_bonus(d):
    return P["mom_w"] * w.MOM[d]


def mom_update(d):
    k = P["mom_decay"]
    m = w.MOM
    for i in range(4):
        m[i] = k * m[i] + (1.0 - k) * (1.0 if i == d else 0.0)


# ---------------------------------------------------------------- phase overrides
BASE = dict(P)
CUR = [None]


def apply_phase_overrides():
    """P['phase_over'] = {'open': {...}, 'mid': {...}, 'end': {...}}: per-phase
    parameter sets layered over the base policy (ablation: empty dict = host)."""
    po = BASE.get("phase_over")
    if not po:
        return
    ph = phase.phase()
    if CUR[0] == ph:
        return
    CUR[0] = ph
    P.clear()
    P.update(BASE)
    P.update(po.get(ph, {}))
    ev("phase_" + ph)


# ---------------------------------------------------------------- congestion
def corridor_penalty(h, nb):
    """Entering a cell with at most one onward free exit while another allied
    head is close: the classic jam in 1-wide lanes and fountain boxes."""
    own = set(nb)
    free = 0
    for n in w.dest(h):
        if n >= 0 and n not in own and n not in w.occ:
            free += 1
    if free > 1:
        return 0.0
    r = P["cong_near"]
    for hc, hid in w.ally_heads:
        if w.tdist(hc, h) <= r:
            ev("corridor")
            return P["cong_pen"]
    return 0.0
