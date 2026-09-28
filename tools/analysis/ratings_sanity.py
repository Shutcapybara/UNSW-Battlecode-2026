"""Rating-table sanity (Q10): evidence tiers, shrinkage, and the join to live shares.

    python -m tools.analysis.ratings_sanity --ratings experiment_data/bot-ratings/latest.json [--state LIVE/state/state.json] [--k 60]

score_shrunk = (n_eff·score + k·μ) / (n_eff + k), n_eff = fixtures × map-weight coverage × min(1, opponents/5) × min(1, maps/8),
μ = mean score of Established bots. Prints the raw and shrunk top-15, the tier counts, and — when the live record is
given — the five live-tested sources with both scores and the Spearman correlations.
"""
import argparse
import json

import numpy as np
import pandas as pd

SOURCES = {'fenrir-v18-arrival-ready-beds': 9508, 'bifrost-v01-portal-memory': 8540, 'ein-dog-v02-momentum': 9639, 'yuna-v02-core': 9663, 'tidus-t02-spread-only': 9980, 'yuna-v03-core': 10013}


def table(ratings, k=60.0):
    B = pd.DataFrame([{c: b[c] for c in ('id', 'name', 'score', 'low', 'high', 'established', 'games', 'opponents', 'maps', 'map_weight_coverage')} for b in ratings['bots']])
    mu = B[B.established].score.mean()
    B['n_eff'] = B.games * B.map_weight_coverage * np.minimum(1, B.opponents / 5) * np.minimum(1, B.maps / 8)
    B['score_shrunk'] = (B.n_eff * B.score + k * mu) / (B.n_eff + k)
    B['rank_raw'] = B.score.rank(ascending=False).astype(int)
    B['rank_shrunk'] = B.score_shrunk.rank(ascending=False).astype(int)
    return B.sort_values('score', ascending=False).reset_index(drop=True), mu


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ratings', required=True)
    ap.add_argument('--state')
    ap.add_argument('--k', type=float, default=60.0)
    args = ap.parse_args()
    ratings = json.load(open(args.ratings))
    B, mu = table(ratings, args.k)
    print(f"bots {len(B)}, established {int(B.established.sum())}, sparse {int((~B.established).sum())}, mean established score {mu:.3f}, k={args.k}")
    print(f"first established raw rank: {int(B[B.established].rank_raw.min())}; top-20 sparse share raw {(~B.head(20).established).mean():.2f}, "
          f"shrunk {(~B.sort_values('score_shrunk', ascending=False).head(20).established).mean():.2f}")
    cols = ['name', 'score', 'score_shrunk', 'games', 'opponents', 'maps', 'map_weight_coverage', 'established', 'rank_raw', 'rank_shrunk']
    print('\n## Top 15 by shrunk score\n')
    print(B.sort_values('score_shrunk', ascending=False).head(15)[cols].round(3).to_markdown(index=False))
    if args.state:
        from scipy import stats
        from .live_record import games_table, load_state
        df = games_table(load_state(args.state))
        live = df[(df.verified == True) & (df.origin == 'controlled') & (df.side == 'A')]  # noqa: E712
        field = live[live.pool == 'field']
        sub = B[B.name.isin(SOURCES)].copy()
        sub['submission'] = sub.name.map(SOURCES)
        sub['live_field'] = sub.submission.map(field.groupby('submission').score.mean())
        sub['live_field_n'] = sub.submission.map(field.groupby('submission').size())
        sub['live_all'] = sub.submission.map(live.groupby('submission').score.mean())
        sub['live_all_n'] = sub.submission.map(live.groupby('submission').size())
        print('\n## Live-tested sources\n')
        print(sub[cols[:3] + ['rank_raw', 'rank_shrunk', 'live_field', 'live_field_n', 'live_all', 'live_all_n']].round(3).to_markdown(index=False))
        s5 = sub.dropna(subset=['live_field'])
        print(f"\nSpearman local score vs live field share (n={len(s5)}): raw {stats.spearmanr(s5.score, s5.live_field)[0]:+.2f}, shrunk {stats.spearmanr(s5.score_shrunk, s5.live_field)[0]:+.2f}")


if __name__ == '__main__':
    main()
