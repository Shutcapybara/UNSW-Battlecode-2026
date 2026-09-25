# tew-v12-mid-support

Lineage: Tew. Parent: `tew-v11-close-support`; policy base `ouroboros-v13-ladder`.

Hypothesis: the full-view support count in v10 outperformed the two-step count in v11 against their direct match (v11 3–5) and hunter-v20 (v10 5–3, v11 4–4). A four-step radius may retain nearby support while rejecting more distant heads.

Change: `ladder_support_radius=4`, with all other policy settings matching v10/v11.

Comparison: native, both sides on `default_small`, `arena`, `devil`, and `schooltime`, against v10 and hunter-v20. See measured results below. No sandbox check.


## Measured results

Native comparison, `experiment_data/tew-v12-mid-support_20260925053451143328` (config frozen in that run): 9–0–7 over 16 games, no runtime faults. It tied v10 4–4 and scored 5–3 against hunter-v20 across `default_small`, `arena`, `devil`, and `schooltime`, both sides. Radius four matched v10's 5–3 against hunter-v20 on the same map set, with no direct advantage over v10. No sandbox test.
