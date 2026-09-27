# Loki family

## v01 — Bifröst v01 teacher ranker

Loki v01 is an exact copy of `bots/bifrost-v01-portal-memory` with a learned
candidate-score bonus added in `main.py`. All non-trained policy behavior comes
from Bifröst v01. Later Bifröst snapshots and Fafnir are excluded.

The trainer targets team 龙虎豹's exact ranked submission **#7771**, side A,
using games 374088–374092 against calc and 375323–375327 against SHINK AI 6500.
The replays, SHA-256 values, and extraction totals are recorded in
`experiment_data/loki-v01-teacher-ranker/replay_manifest.json` and
`training_summary.json`. `lineage.json` records the source hashes and verifies
which Python files remain byte-identical to Bifröst v01.

### Features and candidate coverage

The replay event stream supplies labels and advances the simulated game state.
Before feature generation, the extractor limits other dragons, pearls, and
portal knowledge to the actor's 7×7 observation. It uses the actor's own visible
body chain, observed turn age, current length, public unit count, local heads,
local pearls, and candidate-specific movement/split consequences. Hidden enemy
lengths and remote state are not model inputs. Sonar messages and echoes are
omitted from the learned feature vector; Bifröst v01 still handles them at
runtime.

Bifröst v01's candidate menu contained the recorded action in 136,069 of
136,760 teacher turns (99.5%). The 691 unsupported actions outside the candidate conditions were not used
as labels. The training sample contains 28,931 decision groups: every
supported split and a deterministic one-in-five sample of supported movement
turns. Split groups are downweighted to account for that sampling choice.

The exported classifier has 48 depth-two gradient-boosted trees over 28
features. `trained_model.py` is 13 KB and its inference uses only the Python
standard library. Training uses scikit-learn 1.9.1 from the project `.venv`.
The learned score is added at scale 0.5 to Bifröst's existing action score;
Bifröst's collision simulation, score penalties, candidate generation, and fallback remain in place.

### Held-out action imitation

The two ranked series were held out as whole groups, avoiding games from one
series on both sides of a split:

| Held-out games | Groups | Teacher action ranked first | Uniform candidate reference | Split action ranked first |
| --- | ---: | ---: | ---: | ---: |
| 374088–374092 vs calc | 17,249 | 64.1% | 21.9% | 57.4% |
| 375323–375327 vs SHINK AI 6500 | 11,682 | 70.3% | 23.2% | 55.4% |

These are held-out behavior-cloning metrics for the learned ranker alone, not
for the integrated Bifröst-plus-model score and not match outcomes. They indicate
the features carry signal about the teacher's choices. Loki has not yet been
run in a Battlecode game or judge sandbox, so integrated imitation, win rate,
and CPU margin remain unknown.

### Reproduction

Training code and feature extraction live in `tools/loki/`. Install the optional
fitting package only in the repository `.venv`, then run `tools/loki/train.py`
with the ten replay files listed in the manifest. The bot itself needs no
third-party inference package.
