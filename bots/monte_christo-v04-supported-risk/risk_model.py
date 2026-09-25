"""Cheap fitted hazard, blended with the baseline under distribution shift.

Training covers only selected moves; calibrated prediction is not proof about
untaken actions. Keep half the original prior and verify by actual matches.
"""
from math import exp
from trained_model import MODEL
from risk_features import vector, bucket, prior
from params import P


# Training support is part of the frozen artifact. Do not extrapolate the
# small-dragon exposure data to crowns or scarcely observed trade classes.
SUPPORT = (218, 249, 37, 380, 177, 8, 354, 13, 0)


def probability(raw):
    if raw[1] > 8 or raw[5] >= 380 or SUPPORT[bucket(raw)] < 30:
        return prior(raw)
    if MODEL["kind"] == "table":
        fitted = MODEL["table"][bucket(raw)]
    else:
        z = sum(a*b for a,b in zip(MODEL["weights"], vector(raw)))
        fitted = 1.0 / (1.0 + exp(-max(-30.0, min(30.0, z))))
    mix = P["risk_blend"]
    return max(0.02, min(0.98, (1.0-mix)*prior(raw) + mix*fitted))
