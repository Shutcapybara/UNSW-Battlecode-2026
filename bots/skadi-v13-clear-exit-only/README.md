# Skadi v13: clear exit only

Parent: Skadi v12, based on Gavroche V54. A recently surveyed clear hidden
portal exit uses risk 0.15; an unseen or recently occupied exit uses V54's
baseline risk 1.0. This isolates the value of clear-landing evidence from the
broader unseen-exit discount in v12.

On the standard six-map panel, v13 scored 79–41 including its 8–4 direct record
against V54. On the 108 shared non-self fixtures, v13 scored 71–37 versus
V54's 69–39. Paired outcomes improved on 8 fixtures and worsened on 6. The
fixture seeds match, but bot-internal random choices are not seeded by the
harness. This misses the project's +4 net promotion gate. Per the request to
stop after this iteration, no fresh holdout or CPU screen was run; v13 is not a
confirmed upgrade.

Report: `experiment_data/skadi-v13-clear-exit-only_20260928040905425814`.
V54 paired control: `experiment_data/gavroche-final_20260928032911316538`.
