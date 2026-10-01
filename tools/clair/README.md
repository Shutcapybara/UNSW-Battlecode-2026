# Clair (H-1) harness

Copied from `tools/rc/` (Gustave) with the run root moved to `build/clair/runs` and the frozen gen reference
copied along. Same D-032 gate: `lane.py run/score/extract/cpu`; `score_extra.py` adds the two gate-audit
quantities (combined-panel bootstrap with equal map weights; endgame tier: longest/total margin at end,
round-limit losses with a material lead).

    PY=/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.venv/bin/python
    UNSWBC=$PY's dir/unswbc'  $PY tools/clair/lane.py run <bot> --panel both --seeds 1,2,3 --jobs 9
                                  $PY tools/clair/lane.py score <bot> --parent hb1-14-prior-r540
                                  $PY tools/clair/score_extra.py <bot> --parent hb1-14-prior-r540
