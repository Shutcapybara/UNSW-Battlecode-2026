"""TEMPORAL layer: game phase, bounded schedules and gate audit.

Uses the global round w.RND (identical for every dragon, including children born
late: a child never restarts the opening) and the fixed horizon R = 500.
Dragon age (w.RND - w.BORN) is a separate feature and never substitutes for time.

phase():    'open' for r < t1, 'mid' for t1 <= r < t2, 'end' for r >= t2.
weight(k):  per-mechanism schedule in [0, 1]:
            mode 'hard'  -> 1.0 inside [from, until), else 0
            mode 'ramp'  -> clipped linear ramp from 0 at `from` to 1 at `from + width`,
                            falling back to 0 over `width` before `until`
Every gate decision can be traced (P['phase_trace']) as LOG lines for audits.
"""
import world as w
from params import P

R = 500
GATES = {}


def progress():
    return w.RND / R


def remaining():
    return R - w.RND


def phase():
    r = w.RND
    if r < P["ph_t1"]:
        return "open"
    if r < P["ph_t2"]:
        return "mid"
    return "end"


def weight(key):
    """Schedule weight for mechanism `key` (params key_from/key_until/key_width/key_mode)."""
    r = w.RND
    a = P.get(key + "_from", 0)
    b = P.get(key + "_until", R + 1)
    mode = P.get(key + "_mode", "hard")
    if mode == "hard":
        v = 1.0 if a <= r < b else 0.0
    else:
        wd = max(1, P.get(key + "_width", 40))
        up = (r - a) / wd
        down = (b - r) / wd
        v = max(0.0, min(1.0, up, down))
    GATES[key] = v
    return v


def by_phase(key):
    """Per-phase constant: params key_open / key_mid / key_end."""
    return P[key + "_" + phase()]


def rng(*salt):
    """Deterministic per-(dragon, salt) uniform in [0, 1): reproducible games."""
    h = (w.ME * 0x9E3779B1) & 0xFFFFFFFF
    for s in salt:
        h = ((h ^ (s & 0xFFFFFFFF)) * 0x85EBCA6B) & 0xFFFFFFFF
        h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967296.0
