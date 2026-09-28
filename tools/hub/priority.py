"""Candidate priority score (Part B §8.1). Every term is reported so a reviewer can override with a note."""
import time

WEIGHTS = dict(live_pool_local_score_z=100, diversity=40, novelty=30, headroom=20, replay_link=25, disagreement=30,
               coverage=20, recent_lineage_penalty=-60, already_rejected_same_mechanism=-200)


def score(candidate, ctx):
    """candidate: hub candidates row (dicts for JSON columns). ctx: dict built by the cycle:
    incumbent_lineage, lineage_last_live (lineage -> epoch of last screen/confirmation), lineage_live_games (lineage -> n controlled games),
    lineage_rejected_mechanisms (lineage -> set of mechanism strings rejected), probes (name -> dict max_points/p99_points/live_max),
    finding_ids (set), disagreements (lineage -> pp), local_z (name -> z or None).
    """
    now = ctx.get('now', time.time())
    lineage = candidate.get('lineage') or ''
    terms = {}
    terms['live_pool_local_score_z'] = ctx.get('local_z', {}).get(candidate['name']) or 0.0
    last_live = ctx.get('lineage_last_live', {}).get(lineage)
    if not last_live or now - last_live > 86400:
        terms['diversity'] = 1.0
    elif lineage != ctx.get('incumbent_lineage'):
        terms['diversity'] = 0.5
    else:
        terms['diversity'] = 0.0
    novelty = (candidate.get('novelty') or '').lower()
    terms['novelty'] = {'structural': 1.0, 'new_mechanism': 1.0, 'whole_policy': 0.5}.get(novelty, 0.0)
    probe = ctx.get('probes', {}).get(candidate['name']) or {}
    if probe.get('live_max') and probe['live_max'] >= 95_000_000:
        terms['headroom'] = -1.0
    elif probe.get('max_points') is None:
        terms['headroom'] = 0.0
    elif probe['max_points'] < 70_000_000 and (probe.get('p99_points') or 0) < 50_000_000:
        terms['headroom'] = 1.0
    elif probe['max_points'] < 80_000_000 and (probe.get('p99_points') or 0) < 60_000_000:
        terms['headroom'] = 0.5
    else:
        terms['headroom'] = -0.5
    text = ' '.join(str(candidate.get(k) or '') for k in ('hypothesis', 'mechanism', 'expected_change'))
    terms['replay_link'] = 1.0 if any(fid and fid in text for fid in ctx.get('finding_ids', ())) else 0.0
    terms['disagreement'] = 1.0 if abs(ctx.get('disagreements', {}).get(lineage, 0.0)) > 15 else 0.0
    n_live = ctx.get('lineage_live_games', {}).get(lineage, 0)
    terms['coverage'] = 1.0 if n_live == 0 else 0.5 if n_live < 30 else 0.0
    terms['recent_lineage_penalty'] = 1.0 if (last_live and now - last_live <= 86400) else 0.0
    rejected = ctx.get('lineage_rejected_mechanisms', {}).get(lineage, set())
    mech = (candidate.get('mechanism') or '').strip().lower()
    terms['already_rejected_same_mechanism'] = 1.0 if (mech and mech in rejected) else 0.0
    total = sum(WEIGHTS[k] * v for k, v in terms.items())
    return round(total, 1), terms
