"""Small dependency-free runtime for the early-game fitted-Q policy.

The training script writes a JSON model whose feature contract is the same
numeric row produced by ``tools/team_recon_claude/features_v4.py``.  This
module is deliberately standard-library-only so it can be copied into a bot
without bringing scikit-learn or numpy into the metered process.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ACTION_NAMES = ("F", "R", "B", "L", "split")
CANDIDATE_ATTRIBUTES = (
    "block", "portal", "pearl", "cd", "eh_adj", "area", "pdist", "pmass",
    "pc3", "bedsoon", "unvisited", "allyh2", "eseg2", "run", "mem_bed",
    "mem_bed_n", "mem_pearl",
)


def _number(value, default=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return float(default)
    return value if math.isfinite(value) else float(default)


class EarlyGameQPolicy:
    """Load and score an exported linear fitted-Q policy."""

    def __init__(self, model):
        self.model = model
        self.context_features = tuple(model["context_features"])
        self.actions = tuple(model.get("actions", ACTION_NAMES))
        self.candidate_attributes = tuple(
            model.get("candidate_attributes", CANDIDATE_ATTRIBUTES)
        )
        self.feature_names = tuple(model["feature_names"])
        self.mean = tuple(float(x) for x in model["mean"])
        self.scale = tuple(float(x) or 1.0 for x in model["scale"])
        self.coef = tuple(float(x) for x in model["coef"])
        self.intercept = float(model["intercept"])

    @classmethod
    def load(cls, path):
        return cls(json.loads(Path(path).read_text()))

    def _candidate(self, state, action):
        if action != "split":
            return {
                key: _number(state.get("c%s_%s" % (action, key)), 0.0)
                for key in self.candidate_attributes
            } | {"split_size": 0.0}

        # Split has no landing tile.  The explicit action bit and split size
        # carry the useful information; neutral candidate values prevent the
        # model from treating a split as a mystery portal or a blocked step.
        size = state.get("split_size", state.get("y_split", 2))
        size = _number(size, 2.0)
        return {
            key: 0.0 for key in self.candidate_attributes
        } | {"split_size": size if size >= 2 else 2.0}

    def vector(self, state, action):
        cand = self._candidate(state, action)
        values = []
        for name in self.context_features:
            if name == "phase_0_50":
                value = _number(state.get("round"), 0) < 50
            elif name == "phase_50_100":
                r = _number(state.get("round"), 0)
                value = 50 <= r < 100
            elif name == "phase_100_250":
                r = _number(state.get("round"), 0)
                value = 100 <= r < 250
            elif name == "round_frac":
                value = _number(state.get("round"), 0) / 500.0
            elif name == "is_portal_view":
                value = _number(state.get("vis_portal"), 0) > 0
            else:
                value = _number(state.get(name), 0)
            values.append(float(value))
        values.extend(1.0 if action == name else 0.0 for name in self.actions)
        values.extend(cand.get(name, 0.0) for name in self.candidate_attributes)
        values.append(cand["split_size"])
        return values

    @staticmethod
    def legal_actions(state):
        actions = []
        for action in ("F", "R", "B", "L"):
            # Kelp is the one unambiguously illegal candidate in the v4 view.
            # Unknown portal destinations remain legal: the deployed bot must
            # be allowed to learn whether a portal is worth taking.
            if _number(state.get("c%s_block" % action), 0) != 1:
                actions.append(action)
        length = _number(state.get("length"), 0)
        units = _number(state.get("units"), 0)
        limit = _number(state.get("unit_limit"), 64)
        if length >= 4 and units < limit:
            actions.append("split")
        return actions or ["F"]

    def score(self, state, action):
        vector = self.vector(state, action)
        total = self.intercept
        for value, mean, scale, coefficient in zip(
            vector, self.mean, self.scale, self.coef
        ):
            total += ((value - mean) / scale) * coefficient
        return total

    def rank(self, state):
        return sorted(
            ((action, self.score(state, action))
             for action in self.legal_actions(state)),
            key=lambda item: item[1],
            reverse=True,
        )

    def choose(self, state):
        return self.rank(state)[0][0]


def load_policy(path):
    return EarlyGameQPolicy.load(path)
