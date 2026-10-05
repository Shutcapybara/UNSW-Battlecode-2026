# D-058 §B precedent table — source check (Sugawara, council, mechanism seat)

4 Oct 2026 ~20:50Z. Assigned by D-058 §B / BOARD 19:35Z, due 21:30Z. Method: web search + fetch of primary or
near-primary sources (arXiv/PMLR papers, winners' repos, organiser pages). Kaggle discussion and write-up pages are
rendered by JavaScript and returned no body to the fetcher, so claims that rest only on Kaggle forum posts are marked
**unverified (no body)**, not refuted. Nishinoya's 19:48Z cross-check is consistent with what follows except where
noted in row 2.

## Verdict per row

| Row | Chair's claim | Status | Source and what it says |
|---|---|---|---|
| Hungry Geese (2021) | winner: self-play RL, torus CNN, look-ahead at play time | **Partly verified.** Self-play RL winner: verified. Torus CNN and look-ahead at play time: **unverified** — no fetched source states play-time search for the 1st place. | HandyRL README (github.com/DeNA/HandyRL): "The 1st place solution in Hungry Geese (Kaggle)". AIsmiley news (aismiley.co.jp/ai_news/kaggle-hungry-geese-dena-quantum/): team HandyRL (DeNA / QUANTUM) won 1st of 875 by reinforcement learning; "the majority of the learning process used [QUANTUM's] machines" — i.e. dedicated compute. |
| Hungry Geese | many high places by imitating top-rated episodes, rating filter, symmetry augmentation, ensembles | **Unverified (no body).** The 11th-place write-up title says "NN+MCTS" (kaggle.com/competitions/hungry-geese/writeups/…-approach-11); its body did not load. Treat the imitation recipe as plausible, not sourced. | — |
| Lux S1 (2021) | 1st by self-play RL at scale | **Verified.** | arXiv 2402.08112 (Goodfriend, microRTS): "The first season Lux AI winning DRL agent by Pressman et al. (2021) … GridNet action space, reward shaping, and an actor-critic training algorithm." arXiv 2301.01609 (Chen, Tao et al.) names Toad Brigade as the 1st place and reports a later self-play system beating it 90 % with **one V100 and 600 CPU cores, ~5 M episodes** — the scale self-play needed here. |
| Lux S1 | several next places by imitating the winner's replays with per-unit heads | **Partly verified, overstated.** Imitation of Toad Brigade's replays is documented, but the one source found placed **93rd of 1,178** (github.com/Epicato/lux-AI, U-Net BC on Toad Brigade episodes). "Several of the next places" is unsourced. Nishinoya's "Toad Brigade bootstrapped by imitation before self-play" has **no source** I could find; arXiv 2402.08112 describes it as DRL with reward shaping. Do not cite it as an imitation-then-RL precedent. | as cited |
| Lux S2 (2023) | rule-based at the top, RL below | **Verified.** | arXiv 2402.08112: "Rules-based agents won Halite, Kore, and Lux AI Season 2"; "the top DRL agent by Limburg (2023) in Lux AI Season 2 used a 'DoubleCone' backbone". |
| Halite IV (2020) | rule-based at the top | **Verified.** | github.com/ttvand/Halite README: "winning submission"; repo holds rule-based and deep-learning folders and points to the forum thread on "the rule based strategy" (kaggle.com/c/halite/discussion/183543); arXiv 2402.08112 as above. |
| Kore (2022) | rule-based at the top | **Verified** (arXiv 2402.08112 sentence above). | |
| Halite IV, Kore | imitation entries inside the top ten | **Unverified (no body).** An imitation Kore repo exists (github.com/khanhvu207/kore2022) with no placing stated. | |
| Battlecode (MIT) | hand-written heuristics, no learned component | **Verified for the ladder top as described by participants**; "with search" is unsourced. | blog.stoneztao.com/posts/bc21 (9th, 2021): "Every single bot submitted to Battlecode (that performs well) is effectively a giant … decision tree"; ML "usually near impossible to use". |
| Battlesnake | heuristics with search | **Not checked** (no fetched source this unit). | |
| Pommerman (NeurIPS 2018) | search won; partial observation, teams | **Verified.** | PMLR v101 Osogami & Takahashi: real-time tree search with pessimistic scenarios "won the first and third places". arXiv 1812.07297: a learned agent was "the top 1 learning agent" in "a partially observable multi-agent environment with no communication" — so learning placed, below search. |
| (missing row) IEEE microRTS 2023 | — | **Add.** Closest precedent for clone→RL at small compute. | arXiv 2402.08112: "RAISocketAI is the first DRL agent to win the IEEE microRTS competition" after scripted agents won the five previous; "Behavior Cloning and fine-tuning these models with DRL has proven promising as an efficient way to bootstrap models". |

## Exact changes to D-058 §B (amend)

1. Hungry Geese "What won": "self-play reinforcement learning (HandyRL), with dedicated compute" — drop "torus CNN
   and look-ahead at play time" and mark the imitation sub-claim unverified.
2. Lux S1: "first place by self-play deep RL (actor-critic, per-cell action map, reward shaping); imitation of the
   winner's replays reached mid-table (one documented case, 93/1,178)". Strike "several of the next places".
3. Halite IV / Kore: keep rule-based winners; mark "imitation inside the top ten" unverified.
4. Add microRTS 2023 (DRL won after five scripted wins; BC→DRL fine-tuning reported as an efficient bootstrap).
5. Reading 1 holds and is strengthened: of eight contests checked, the verified winners are rule/search-based in
   five (Lux S2, Halite IV, Kore, Battlecode, Pommerman) and self-play DRL in three (Hungry Geese, Lux S1, microRTS),
   and every verified DRL win carries dedicated compute or many iterations. Reading 2 ("how imitation was done
   where it worked") is the weakest part of the table: **no verified source shows imitation alone winning or
   placing top-ten in these contests.** D-059 (this contest's top teams use networks) is now the main support for
   the clone-first line, not the Kaggle table.

## Effect on rulings

- None of the corrections reverses D-058 §C.1 (clone first) or D-059. They weaken §C.3's claim that the rating-filter /
  teacher-conditioned recipe is precedent-backed: A6/A7 rest on our own evidence plus plausibility, which is fine
  under D-058 §A as long as the cards say so.
- They strengthen P-7's premise: every DRL winner fine-tuned or trained by self-play; none stopped at a clone.

## Dissent / limits

- Kaggle forum bodies were unreadable; a human with a browser can upgrade the four "unverified (no body)" cells in
  minutes. I did not use memory to fill them.
