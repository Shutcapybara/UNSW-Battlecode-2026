"""Bot x map performance matrix + loss-mode decomposition for top bots."""
import duckdb
import pandas as pd
import numpy as np

con = duckdb.connect()
df = con.execute("SELECT bot_a, bot_b, map, outcome, rounds FROM read_parquet('game_stats.parquet')").df()

MAIN = ['Colosseum','arena','autarky','big_empty','default','default_small','devil',
        'dilemma','queen_of_spades','schooltime','stronghold','trauma','trophy']

# long-format team-game records
recs = []
for a, b, mp, o, r in zip(df.bot_a, df.bot_b, df['map'], df.outcome, df.rounds):
    if mp not in MAIN:
        continue
    recs.append((a, mp, 1 if o == 'A' else 0.5 if o == 'draw' else 0, r, o != 'draw'))
    recs.append((b, mp, 1 if o == 'B' else 0.5 if o == 'draw' else 0, r, o != 'draw'))
long = pd.DataFrame(recs, columns=['bot', 'map', 'score', 'rounds', 'decisive'])
long['win'] = (long.score == 1).astype(int)
long['loss'] = (long.score == 0).astype(int)
long['loss_at_limit'] = ((long.score == 0) & (long.rounds >= 495)).astype(int)
long['loss_early'] = ((long.score == 0) & (long.rounds < 100)).astype(int)

ratings = pd.read_csv('experiment_data/meta/bt_ratings.csv')
top = ratings[ratings.games >= 300].head(28).bot.tolist()

sub = long[long.bot.isin(top)]
pv = sub.pivot_table(index='bot', columns='map', values='score', aggfunc='mean')
cnt = sub.pivot_table(index='bot', columns='map', values='score', aggfunc='count')
pv = pv[MAIN]

# residual vs bot's own mean over these maps (controls opponent strength only roughly)
bot_mean = sub.groupby('bot').score.mean()
resid = pv.sub(bot_mean, axis=0)

pd.set_option('display.width', 250)
print('=== mean score by map (top bots) ===')
print(pv.round(2).to_string())
print()
print('=== residual vs own mean ===')
print(resid.round(2).to_string())
print()
print('=== games per map per bot (min should be decent) ===')
print(cnt[MAIN].min(axis=1).describe())

# loss modes for top bots
lm = sub.groupby('bot').agg(
    games=('score', 'count'), wr=('score', 'mean'),
    losses=('loss', 'sum'),
    loss_limit=('loss_at_limit', 'sum'), loss_early=('loss_early', 'sum'))
lm['limit_share'] = (lm.loss_limit / lm.losses.clip(lower=1)).round(2)
lm['early_share'] = (lm.loss_early / lm.losses.clip(lower=1)).round(2)
print()
print('=== loss modes (top bots) ===')
print(lm.sort_values('wr', ascending=False).to_string())

# map tempo: elimination vs limit
mt = long.groupby('map').agg(games=('score','count'), mean_rounds=('rounds','mean'),
                             decisive=('decisive','mean'))
lim = long[long.rounds >= 495].groupby('map').size() / long.groupby('map').size()
mt['limit_frac'] = lim.round(3)
print()
print('=== map tempo ===')
print(mt.round(2).to_string())

pv.to_csv('experiment_data/meta/bot_map_scores.csv')
resid.to_csv('experiment_data/meta/bot_map_residuals.csv')
lm.to_csv('experiment_data/meta/loss_modes.csv')
mt.to_csv('experiment_data/meta/map_tempo.csv')
