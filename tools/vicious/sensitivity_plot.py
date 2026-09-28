"""Plot frozen finalist timing checks on their matched diagnostic fixtures."""
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/vicious-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
C = Path(json.loads((ROOT / 'tools/vicious/current.json').read_text())['directory'])
carrier = json.loads((C / 'cycle_05/CARRIER_SENSITIVITY.json').read_text())
feed = json.loads((C / 'cycle_05/FEED_SENSITIVITY.json').read_text())
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
panels = [
    (carrier, [
        ('vicious-x22-carrier-340', '340'),
        ('vicious-x12-crown-clear', '380\nfinalist'),
        ('vicious-x23-carrier-420', '420'),
        ('vicious-x24-carrier-static', '500\nstatic')],
     'Small-crown foraging cutoff', 'Orchard: two opponents; Big Empty: v32\nBoth sides · six games per arm'),
    (feed, [
        ('vicious-x25-feed-320', '320'),
        ('vicious-x15-late-time', '340\nfinalist'),
        ('vicious-x26-feed-360', '360'),
        ('vicious-x27-feed-soft', '340–400\nsoft')],
     'Receiver preparation schedule', 'Stronghold and Big Empty versus v32\nBoth sides · four games per arm')]
for ax, (data, items, label, title) in zip(axes, panels):
    values = [data[key]['wins'] + .5 * data[key]['draws'] for key, _ in items]
    n = data[items[0][0]]['games']
    assert all(data[k]['games'] == n for k, _ in items)
    ax.bar(range(len(items)), values,
           color=['#176f83' if 'finalist' in lab else '#929aa4' for _, lab in items])
    for i, score in enumerate(values):
        ax.text(i, score + .1, f'{score:g}/{n}', ha='center', va='bottom')
    ax.set_xticks(range(len(items)), [lab for _, lab in items])
    ax.set_ylim(0, n + .8); ax.set_yticks(range(n + 1))
    ax.set_ylabel('Wins + ½ draws'); ax.set_xlabel(label + ' · global round')
    ax.set_title(title, fontsize=10); ax.grid(axis='y', alpha=.15); ax.set_axisbelow(True)
fig.suptitle('Postselection timing checks · finalists remain unchanged', fontsize=13)
fig.tight_layout(rect=(0, .06, 1, .94))
fig.text(.5, .02, 'Small diagnostic panels, not independent confirmation. “Static” changes only the new carrier cutoff.',
         ha='center', fontsize=9, color='#555')
for extension in ('png', 'svg'):
    fig.savefig(C / 'figures' / ('timing_sensitivity.' + extension), dpi=170)
