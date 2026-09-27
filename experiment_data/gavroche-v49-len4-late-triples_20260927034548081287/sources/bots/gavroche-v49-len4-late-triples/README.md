# Gavroche V46 early CPU budget

Parent: V45. The dense-phase sprint limit is 4 throughout. From round 150,
sparse-phase triple candidates are disabled, target search is capped at 32
nodes, and long-body safety floods are capped at 24 cells.

The four-game judge-sandbox screen passed the conservative CPU gate without
faults: p99 42.2–46.1M and maximum 68.5–75.4M. The seeded 108-game native
family panel scored 59–49 with no faults, including 32–16 against
Sinbad/tf05/grad1/x04. It trails V36 strategically, especially on Big Empty
and Stronghold, so continue tuning before considering it a final candidate.

Native panel: `experiment_data/gavroche-v46-early-budget_20260927021339967439`.
CPU screen: `experiment_data/gavroche-v46-sandbox-cpu_20260927230000000000`.
