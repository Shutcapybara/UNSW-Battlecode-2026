"""Shared global-time facts for Ed's bounded 500-round horizon."""
HORIZON = 500


def phase_state(round_n, opening_end, endgame_start):
    if not (0 <= opening_end < endgame_start < HORIZON):
        raise ValueError("phase boundaries must satisfy 0 <= t1 < t2 < horizon")
    if round_n < opening_end:
        phase, reason = "opening", "global round < opening_end"
    elif round_n < endgame_start:
        phase, reason = "middle", "opening_end <= global round < endgame_start"
    else:
        phase, reason = "endgame", "global round >= endgame_start"
    opening_weight = max(0.0, min(1.0,
        (opening_end - round_n) / float(opening_end))) if opening_end else 0.0
    return {"round": round_n, "progress": round_n / float(HORIZON),
            "remaining": HORIZON - round_n, "phase": phase,
            "opening_weight": opening_weight, "reason": reason}
