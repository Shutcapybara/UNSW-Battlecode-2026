"""Shared training/deployment action contract; standard library only.

No map IDs, schedules, portal penalties, or hand-scored movement preferences.
The bounded action vocabulary is a model-capacity choice, not a strategy.
"""
import itertools
import json
import math
import random
import struct

REL = 'FRBL'
ACTIONS = tuple(REL) + tuple(''.join(p) for p in itertools.product(REL, repeat=2)) + (
    'split_min', 'split_half', 'split_max',
)


def split_size(action, length):
    return {'split_min': 2, 'split_half': length // 2, 'split_max': length - 2}[action]


def action_mask(row):
    """Mask invalid/duplicate splits only. Fatal moves remain learnable actions."""
    length = int(row['length'])
    mask, sizes = [], set()
    for action in ACTIONS:
        if action.startswith('split_'):
            size = split_size(action, length)
            legal = (2 <= size <= length - 2 and
                     row['units'] < row['unit_limit'] and size not in sizes)
            mask.append(legal)
            if legal:
                sizes.add(size)
        else:
            # Sprinting can eat before paying its next step. Do not veto a
            # length-2 sprint using only its starting length.
            mask.append(True)
    return mask


def observed_index(row):
    family = row.get('y_family')
    if family == 'move':
        seq = row.get('y_seq')
        return ACTIONS.index(seq) if seq in ACTIONS else None
    if family == 'split':
        for i, action in enumerate(ACTIONS):
            if action.startswith('split_') and action_mask(row)[i]:
                if split_size(action, int(row['length'])) == row.get('y_split'):
                    return i
    return None


def numeric(value):
    value = float(value)
    return value if math.isfinite(value) else 0.0


def float32(value):
    """Round like the float32 feature matrix used to fit exported trees."""
    try:
        return struct.unpack('=f', struct.pack('=f', float(value)))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


class Policy:
    def __init__(self, payload):
        if payload['actions'] != list(ACTIONS):
            raise ValueError('incompatible action vocabulary')
        self.data = payload

    @classmethod
    def load(cls, path):
        with open(path, encoding='utf-8') as stream:
            return cls(json.load(stream))

    def logits(self, row):
        d = self.data
        if 'tree' in d:
            # sklearn's training and apply paths use float32 inputs. Preserve
            # each float32 rounding step so threshold-adjacent rows take the
            # same branch in this dependency-free runtime.
            x = []
            for key, mean, scale in zip(d['features'], d['mean'], d['scale']):
                centered = float32(float32(numeric(row.get(key, 0))) - float32(mean))
                normalized = float32(centered / float32(scale))
                x.append(max(-10.0, min(10.0, normalized)))
            tree, node = d['tree'], 0
            while tree['left'][node] != -1:
                node = tree['left'][node] if x[tree['feature'][node]] <= tree['threshold'][node] else tree['right'][node]
            return tree['logits'][node]
        x = [max(-10.0, min(10.0, (numeric(row.get(k, 0)) - m) / s))
             for k, m, s in zip(d['features'], d['mean'], d['scale'])]
        for index, layer in enumerate(d['layers']):
            x = [bias + sum(w * v for w, v in zip(weights, x))
                 for weights, bias in zip(layer['weight'], layer['bias'])]
            if index != len(d['layers']) - 1:
                x = [max(0.0, v) for v in x]
        return x

    def choose(self, row, temperature=0.0, rng=None):
        scores, mask = self.logits(row), action_mask(row)
        allowed = [i for i, ok in enumerate(mask) if ok]
        if temperature > 0:
            best = max(scores[i] for i in allowed)
            weights = [math.exp(max(-50, (scores[i] - best) / temperature)) for i in allowed]
            return (rng or random).choices(allowed, weights=weights, k=1)[0]
        return max(allowed, key=lambda i: scores[i])
