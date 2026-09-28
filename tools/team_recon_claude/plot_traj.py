import sys, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
TJ = pd.read_csv(sys.argv[1]); out = sys.argv[2]; title = sys.argv[3]; tname = sys.argv[4] if len(sys.argv) > 4 else 'Vibing++'
TJ = TJ[TJ['round'] % 10 == 0]
last = TJ.groupby('game')['round'].max()
fig, ax = plt.subplots(1, 5, figsize=(22, 4))
for i, (col, lab) in enumerate([('units', 'dragons alive'), ('total', 'total length'), ('longest', 'longest dragon'), ('share_longest', 'longest / total')]):
    for who, c in (('t', '#c0392b'), ('o', '#2c3e50')):
        for res, ls in (('W', '-'), ('L', '--')):
            x = TJ[(TJ.who == who) & (TJ.result == res)]
            x = x[x['round'] < x.game.map(last)]  # drop terminal snapshot of eliminated games
            gb = x.groupby('round')[col]
            med = gb.median()
            ax[i].plot(med.index, med.values, ls, color=c, label=f"{tname if who == 't' else 'opponent'} | target {res}")
            if res == 'W':
                ax[i].fill_between(med.index, gb.quantile(.25).values, gb.quantile(.75).values, color=c, alpha=.12)
    ax[i].set_title(lab); ax[i].set_xlabel('round')
for res, ls in (('W', '-'), ('L', '--')):
    g = TJ[TJ.result == res].groupby('game')['round'].max()
    r = np.arange(0, 501, 10)
    ax[4].plot(r, [(g >= k).mean() for k in r], ls, color='k', label=f'target {res} (n={len(g)})')
ax[4].set_title('games still running'); ax[4].legend(fontsize=8)
ax[0].legend(fontsize=7)
fig.suptitle(title); plt.tight_layout(); plt.savefig(out, dpi=100)
