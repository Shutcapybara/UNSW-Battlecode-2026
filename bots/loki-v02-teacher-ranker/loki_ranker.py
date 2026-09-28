"""Small standard-library inference wrapper for the trained candidate ranker."""
import world as w
from loki_features import (
    RANKING_FEATURE_INDICES,
    features,
    from_world,
    prepare_inference,
    rank_features,
)
from params import P
from trained_model import MODEL


_MODEL_FEATURES = frozenset(
    node[0]
    for tree in MODEL["trees"]
    for node in tree
    if node[0] >= 0
)
_USE_SPARSE_FEATURES = _MODEL_FEATURES <= RANKING_FEATURE_INDICES


def _model_score_bounds():
    rate = MODEL["learning_rate"]
    min_leaf = []
    max_leaf = []
    for tree in MODEL["trees"]:
        leaves = [node[4] for node in tree if node[0] < 0]
        min_leaf.append(min(leaves))
        max_leaf.append(max(leaves))
    low = MODEL["bias"] + rate * sum(min_leaf)
    high = MODEL["bias"] + rate * sum(max_leaf)
    return (min(low, high), max(low, high))


_MODEL_SCORE_MIN, _MODEL_SCORE_MAX = _model_score_bounds()
_MODEL_SCORE_SPAN = _MODEL_SCORE_MAX - _MODEL_SCORE_MIN


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
    scale = P["loki_model_scale"]
    if scale == 0.0 or len(actions) < 2:
        return actions

    # A candidate more than the full model-score span behind the base leader
    # cannot win, even under the most favorable possible forest output. Skip its
    # feature work while preserving the full-model argmax exactly.
    top_base = max(score for score, _action in actions)
    competitive_floor = top_base - abs(scale) * _MODEL_SCORE_SPAN

    state = from_world(w)
    feature_builder = features
    if _USE_SPARSE_FEATURES:
        state = prepare_inference(state)
        feature_builder = rank_features
    else:
        state["_loki_dest_cache"] = {}

    ranked = []
    for score, action in actions:
        if score < competitive_floor:
            ranked.append((score, action))
            continue
        learned = raw_score(feature_builder(state, action))
        ranked.append((score + scale * learned, action))
    return ranked
