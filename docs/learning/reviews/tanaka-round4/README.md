# Fourth wake receipts

Synthetic P-2 probes never access real confirmation labels, claims or predictions. `p2_confirm.py` is the exact audited ea3b5ef7 source snapshot. `p2-audit.json` covers gate/receipt behavior and the frozen-exclusion counterexample; `evaluate-audit.json` covers invented numerical data. Owner cell-count metadata is archived separately.

`k16-seed1-pairs.csv` freezes all736 candidate-parent development pairs, keyed by panel,seed,map,opponent,seat. Source queen-table hashes and bootstrap summaries are in k16-seed1-audit.json. No seed2/3 gate data was selected or analyzed.

`rollback-audit.json` contains independent small synthetic verification of the decision formula and frozen sequence counts, not a rerun of the operating-characteristics simulation.

Reproduction helpers in tools/tanaka: p2_release_audit.py, p2_evaluate_audit.py, k16_seed1_audit.py, rollback_rule_audit.py. They use explicit local main/Asahi paths and write only /tmp/tanaka-r4; run from the shared main repository using its .venv/bin/python at nice10 with BLAS threads1. p2_release_audit snapshots the current source; use this directory's archived source for an exact historical check. The evaluator helper reads /tmp/tanaka-r4/p2_confirm.py, created by that helper. No helper invokes a real bot run, confirmation or score.
