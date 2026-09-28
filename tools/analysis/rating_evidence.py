"""A10 — minimum-evidence rule and shrinkage prior for the campaign rating table (handoff §3.10).

Problem (2026-09-28 table): rows with 2 fixtures vs 1 opponent on 1 map outrank rows with
70-122 fixtures ('yuna-x43-local-crown-donor' 78.6% on n=2 at rank 4); the top-26 is entirely
'Sparse'; public correlation of the table with live shares is negative on the seven versions
checked by the director. The model-predicted 'score vs reference panel' extrapolates almost
from the prior for such rows, so raw score cannot order the queue.

Rule implemented here (proposal; patch for tools/benchmark_ratings.py in patches/):
- queue-eligible = established evidence: >= MIN_FIXTURES fixtures AND >= MIN_OPPONENTS
  opponents AND >= MIN_MAPS maps (mirrors the dashboard's 'Sparse' definition);
- display score for ordering = shrunk toward the established-panel mean with weight
  n/(n+N0): shrunk = prior + (score - prior) * n/(n + N0), N0 = 60 fixtures;
- Sparse rows stay visible but are marked display-only.

Unit of independence for the underlying fixtures: the (bot pair, map) cell — already the
dashboard's unit; shrinkage operates on the fixture count, not games.
"""
MIN_FIXTURES = 60
MIN_OPPONENTS = 5
MIN_MAPS = 8
N0 = 60.0


def established(bot):
    """True when the row carries enough direct evidence to be ordered by the table."""
    return (bot.get('games') or 0) >= MIN_FIXTURES and (bot.get('opponents') or 0) >= MIN_OPPONENTS \
        and (bot.get('maps') or 0) >= MIN_MAPS


def panel_prior(bots):
    """Mean raw score of established rows; 0.5 when none exist (no evidence → coin flip)."""
    est = [b['score'] for b in bots if established(b) and b.get('score') is not None]
    return sum(est) / len(est) if est else 0.5


def shrunk_score(bot, prior):
    """Raw score shrunk toward the panel prior with weight n/(n+N0)."""
    score, n = bot.get('score'), bot.get('games') or 0
    if score is None:
        return None
    return prior + (score - prior) * n / (n + N0)


def order_table(bots):
    """Sort rows by (queue-eligible, shrunk score) — eligible rows first, n=2 rows sink."""
    prior = panel_prior(bots)
    keyed = [(established(b), shrunk_score(b, prior) or 0.0, b) for b in bots]
    keyed.sort(key=lambda k: (k[0], k[1]), reverse=True)
    return [dict(bot=k[2], established=k[0], shrunk=round(k[1], 4)) for k in keyed]
