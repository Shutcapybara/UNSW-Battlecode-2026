"""Small standard-library inference wrapper for the trained candidate ranker."""
import world as w
from loki_features import features, from_world
from params import P
from trained_model import MODEL


def raw_score(vector):
    score = MODEL["bias"]
    rate = MODEL["learning_rate"]
    for tree in MODEL["trees"]:
        node = 0
        while tree[node][0] >= 0:
            feature, threshold, left, right, _value = tree[node]
            node = left if vector[feature] <= threshold else right
        score += rate * tree[node][4]
    return score


def rerank(actions):
    state = from_world(w)
    scale = P["loki_model_scale"]
    max_cells = P.get("loki_model_max_cells", 0)
    if max_cells and w.W * w.H > max_cells:
        scale = 0.0
    ranked = []
    for score, action in actions:
        learned = raw_score(features(state, action))
        ranked.append((score + scale * learned, action))
    return ranked
