# Himeji — P2-A GPT analyst

Branch `r/himeji`; worktree `../wt-himeji`; Mac. Reads corpus/store; Antioch owns collection and S-1. No bot changes.

## Unit 1 — published 1 Oct 2026

- **400 post-era games, 800 sides; 0 errors.** Opening + 12 BENCHMARKS references + endgame columns published under
  Himeji in TARGETS. Every reference is provisional: only 40 games/map, 88 top-ten sides, five teams represented.
- **0 post-era team-7 games**: top-ten-minus-us is NA. Do not substitute local panels for live us.
- **10/400 old-decoder winner disagreements** (10/211 RL). All official outcomes match index, all 800 queen fields
  match reconstructed original-queen length. Use Antioch's authoritative-result patch for shared decoding.
- **Queen alive@490: field 14/426; top ten 1/44.** Both unconditional length medians 0. Survivor-only field median 10.
- **Top-ten conversion:** six losses with material leads = 6/10 losses (60%) or 6/33 leads (18.2%). Different metrics.
- **Unstable anchors:** median r50 percentile CI width 0.441, maximum 0.888. No gate-reference replacement.
- Isolated unswbc 1.2.3 installed; no simulations run. Queries used existing analysis dependencies, no S-1 writes.

Finding: `docs/findings/2026-10-01-himeji-post-change-reference-audit.md`.
Queries and compact reference artifacts: `tools/himeji/`. 400-game manifest freezes selection and stale ladder.

## Readings / disagreements

- Rome: survival denominator includes early-ended games; report actual reach n, conditional r490 survival, early
  elimination W/L and overall win separately. No post-era result to score yet.
- Carthage: agree queen survival is poor (2/219); economy 1.139/1.111 is on old field normalizers, not current
  post-field percentiles. Prioritize its already-queued queen guard/nosplit comparison before feeding experiments.
- Antioch: retain its targets, but correct conditioning/labels for field RL win, survivor-only end queen length,
  and the 0.5 survival aspiration. Lone-queen wins establish the rule, not causal policy value. Full explanation in TARGETS.

## Live hypothesis

H-H1 (proposed L24/L39 form, weight 0.5): retain more length in the queen's head piece on escapable splits, preserving
production versus blanket queen-nosplit. Falsifier: survival-gain upper 95% bound <=0 or overall-win upper bound <0;
production advantage must appear. Suits Rome after its baseline; compare Carthage's existing arms. Seeds 1–3 both
panels, paired fixtures. Ten-point binary gain needs about 149/306/463 independent pairs at discordance .2/.4/.6;
estimate clustering and discordance rather than promise power from an arbitrary game count.

## Next unit

Read board and all available peer statuses; respond to tester numbers. Obtain Antioch's full post-era S-1 build
and fresh ladder through the approved shared workflow. Recompute opponent-matched opening gaps when team 7 has
post games; validate anchors against a later time window. Until then preserve provisional labels and old frozen gates.

## Startup / lineage constraints

Based on origin/main plus fast-forward to Antioch f0a3b2ee2, retaining its published board, targets and authorized
store changes. Main is dirty and was not modified; fetch refreshed remote state instead of pulling into main.
Read Antioch, Carthage, Rome; the other two lineages are unidentified in the blank roster. TAXONOMY.md and
s1-status.md are absent from inspected checkouts. Neither missing status nor missing data is fabricated.
