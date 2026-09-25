"""Cheap fitted hazard, blended with the baseline under distribution shift.

Training covers only selected moves; calibrated prediction is not proof about
untaken actions. Keep half the original prior and verify by actual matches.
"""
from math import exp
from trained_model import MODEL
from risk_features import vector, bucket, prior
from params import P


def probability(raw):
    if MODEL["kind"] == "table":
        fitted = MODEL["table"][bucket(raw)]
    else:
        z = sum(a*b for a,b in zip(MODEL["weights"], vector(raw)))
        fitted = 1.0 / (1.0 + exp(-max(-30.0, min(30.0, z))))
    mix = P["risk_blend"]
    return max(0.02, min(0.98, (1.0-mix)*prior(raw) + mix*fitted))
