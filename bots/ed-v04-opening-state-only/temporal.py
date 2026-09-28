"""Small auditable global-time phase interface for Ed experiments."""
HORIZON = 500


def phase_state(round_n, opening_end, endgame_start):
    if not (0 <= opening_end < endgame_start < HORIZON):
        raise ValueError("phase boundaries must satisfy 0 <= t1 < t2 < horizon")
    if round_n < opening_end:
        phase = "opening"
        reason = "global round %d < opening_end %d" % (round_n, opening_end)
    elif round_n < endgame_start:
        phase = "middle"
        reason = "opening_end <= global round %d < endgame_start" % round_n
    else:
        phase = "endgame"
        reason = "global round %d >= endgame_start %d" % (round_n, endgame_start)
    opening_weight = max(0.0, min(1.0,
        (opening_end - round_n) / float(opening_end))) if opening_end else 0.0
    return {
        "round": round_n,
        "progress": round_n / float(HORIZON),
        "remaining": HORIZON - round_n,
        "phase": phase,
        "opening_weight": opening_weight,
        "reason": reason,
    }
