# Loki training tools

`replay_data.py` streams the public replay event format and builds one candidate
set per sampled teacher turn. It keeps the teacher's chosen action only when
that action exists in the Bifröst v01 menu. State features are reconstructed
from visible cells around the actor; full replay state is used only to advance
the event stream and is filtered before feature calculation.

`train.py` fits a shallow `GradientBoostingClassifier`, holds out each ranked
series in turn, checks the exported tree scores against scikit-learn, and writes
`trained_model.py` plus a training summary and replay hashes. It installs no
runtime dependency into the bot.

Use the repository Python environment:

```sh
.venv/bin/python -m pip install 'scikit-learn>=1.6,<2'
.venv/bin/python tools/loki/train.py \
  --teacher-submission 7771 --teacher-side A \
  --replays /path/to/374088.replay /path/to/374089.replay \
           /path/to/374090.replay /path/to/374091.replay /path/to/374092.replay \
           /path/to/375323.replay /path/to/375324.replay \
           /path/to/375325.replay /path/to/375326.replay /path/to/375327.replay
```

The exact replay hashes, sampled action counts, grouped holdout metrics, and
model settings are stored under `experiment_data/loki-v01-teacher-ranker/`.
