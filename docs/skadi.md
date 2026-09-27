# Skadi v01: family synthesis

Skadi (Old Norse **Skaði**) is the new family name, after the Norse figure
associated with hunting and skiing in the mountains. This is a candidate
design record, not a result claim.

## Chassis and selected mechanisms

The chassis is a copy of `bots/gavroche-final` (Gavroche V54), the strongest
Gavroche candidate that completed both a broad seeded panel and the local CPU
screen. V54 uses bounded target search, bounded room floods, and late-phase
caps. Its 108-game panel was 69–39, including 32–16 against Sinbad, tf05,
grad1, and x04. In four judge-sandbox fixtures it had 43.0–44.1M p99 CPU,
52.8–63.7M peaks, and no timeouts. Those results establish the parent only;
Skadi's own CPU and strategy screens are recorded below.

Skadi adds two mechanisms:

1. **Fafnir: size-matched counter-threat support.** Fafnir's f12-sizematch
   composite passed its 32-game screen at 25–7 (+2) and its 182-game gauntlet
   at 140–42 (+6), with a clean four-game sandbox. Skadi applies the same
   attacker-centered condition to Gavroche's probabilistic threat cost: a
   nearby ally counts only if its observed length is at least the attacker's.
   This avoids the false protection of small feeders around a long target.
2. **Scholze: exit guard with a productive-pocket exception.** The Scholze
   v04 report found fewer early casualties on Devil (27 to 21) after guarding
   zero- and one-exit moves. Skadi reuses the cheap local exit count. A
   zero-exit move gets the exception only when the reachable pearl count can
   grow a forager to split length and recover the two segments left behind as
   a trapped parent, the production window remains open, and a small bounded
   search finds enough room for the escape child. A pocket with pearls that
   cannot support that net-length condition does not get the exception.

Gavroche already supplies an opening rescue split, crown election and
feeding, arrival-aware resource values, shared observations, threat scoring,
and the tested target/flood budget. These cover the corresponding Serre
strengths on this chassis. Scholze's opening mechanism is represented by the
inherited rescue path rather than copied as another rule.

## Findings not promoted into the candidate

- **Witten:** x01 portal memory improved one of eight matched fixtures and
  missed its +2 advancement gate. The reset-qualified x03 bed contest fixed
  false activation but scored 1–11 against its control's 2–10. It remains a
  useful guard design, not a proven competitive improvement.
- **Newton:** x10's compact fast-bed contest plus round-200 production stop
  improved the compact specialist panel to 3–5 from 0–8 and the gauntlet to
  147–35 from 140–42. It failed the frozen 32-game screen at 25–7 versus
  25–7; the unconditional stop gave away grind games. The contest and stop
  need state conditioning before they belong in a broad candidate.
- **Serre:** its main contribution is the measurement discipline and the
  arrival-aware, threat-aware, crown-capable baseline inherited conceptually
  by the Gavroche chassis. Its largest diagnosed leak was ceding contested
  center beds and then self-congesting; Witten/Newton's experiments show that
  static bed-value changes alone do not solve that leak safely.
- **Fafnir:** the broader compact-production doctrine stays out. It improved
  the gauntlet, but the strict reserve gate was unchanged because its
  mechanisms did not activate on either frozen reserve map.

## Path and split behavior

The expensive choices remain bounded by Gavroche V54's target-search caps and
late flood caps. Each ordinary move still uses its bounded flood score. Skadi
adds only a four-neighbor exit count to each simulated legal move. It runs the
extra child-room search only after a candidate has zero exits and has enough
counted pearls to reach the split threshold, so open routes do not pay for
that check. Candidate checks share a 24-node-per-decision budget and treat
budget exhaustion as insufficient room.

The productive-pocket test uses only pearls counted by the existing
time-aware flood. It does not assume unseen food. It compares the post-harvest
length after sacrificing a two-segment trapped parent with the current team
length. The child-room check treats that parent body as blocked and stops after
finding the configured child area. This favors safety when the route evidence
is incomplete.

## Benchmark results (2026-09-27)

The four-game judge-sandbox screen against Gavroche V31 completed all 500
rounds with zero reported runtime faults. Candidate CPU by fixture was:

| Map | Candidate side | p99 CPU | Max CPU |
|---|---|---:|---:|
| Big Empty | A | 43.6M | 60.4M |
| Big Empty | B | 43.5M | 59.7M |
| Trauma | A | 43.2M | 51.9M |
| Trauma | B | 43.8M | 53.2M |

This sample passes the project screen of p99 <60M and max <80M. Skadi went
2–2 against V31 on those four fixtures. The CPU run is
`experiment_data/skadi-v01-deadend-guard_20260927103546138035`; its config is
`configs/skadi/sandbox.toml`.

The seeded native panel completed 120/120 games with zero game errors,
analysis errors, or runtime faults. Skadi scored 71–49 overall (59.2%):

| Opponent | W–L |
|---|---:|
| Gavroche V54 (`gavroche-final`) | 7–5 |
| Gavroche V33 | 4–8 |
| Gavroche V31 | 7–5 |
| Gavroche V23 | 8–4 |
| Gavroche V17 | 6–6 |
| Sinbad V07 | 5–7 |
| Von Neumann tf05 | 7–5 |
| Von Neumann grad1 | 7–5 |
| Von Neumann x04 | 10–2 |
| Monte Christo x12 | 10–2 |

Across all ten opponents, map results were Autarky 12–8, Big Empty 12–8,
Queen of Spades 12–8, Schooltime 17–3, Stronghold 11–9, and Trauma 7–13.
The panel shows clear weak spots on Trauma and against V33/Sinbad.

For a like-for-like comparison, the other nine opponents share all 108
opponent/map/side fixtures and exact seeds with the completed V54 panel.
Skadi scored 64–44 on those fixtures; V54 scored 69–39. Outcome changes
favored Skadi on 15 fixtures and V54 on 20, with 73 unchanged. Skadi's 7–5
direct win over V54 is promising, but the shared-panel result does not show an
overall improvement. Keep v01 experimental; do not promote it over V54 yet.
Because the Fafnir support condition and Scholze exit guard were combined,
these results do not identify which change caused the regression. The next
useful comparison is to ablate each mechanism separately.

The native panel is
`experiment_data/skadi-v01-deadend-guard_20260927104356982358`, configured by
`configs/skadi/family-panel.toml`. These native results measure strategy, not
judge CPU; CPU conclusions above come from the separate sandbox run.

## Ablation results (2026-09-27)

To identify which graft caused v01's regression, two variants were copied
directly from V54 and run on the same 108 seeded fixtures:

| Variant | Change | Record | Paired outcome changes vs V54 |
|---|---|---:|---|
| Skadi v02 Fafnir-only | Size-matched counter-threat support | 72–36 | 10 Skadi wins / 7 V54 wins / 91 same |
| Skadi v03 exit-only | Zero-exit guard with productive-split exception; original V54 trap scoring retained | 65–43 | 18 Skadi wins / 22 V54 wins / 68 same |

Fafnir-only is the best measured Skadi branch so far and moves three wins
ahead of V54's 69–39. Its main gains were against V31/V23 and on Big Empty,
Stronghold, and Trauma; it lost ground to Sinbad and on Queen/Schooltime. This
is a positive but small edge, not yet a clear improvement. The current exit
guard regresses by four net wins alone; do not carry its v01 penalty unchanged
into the next candidate. Keep iterating from v02 and tune support conservatively.

Fafnir-only run: `experiment_data/skadi-v02-fafnir-only_20260927110821861817`.
Exit-only run: `experiment_data/skadi-v03-exit-only_20260927112258764987`.
Both use `configs/skadi/ablation-panel.toml` and had 0 game errors, 0 analysis
errors, and 0 runtime faults. These are native strategy runs, not CPU screens.

The radius-two probe did not advance: it scored 24–12 against V31/V23/Sinbad
and tied V54's outcomes on those exact 36 fixtures, while losing three net
outcomes to v02. A stronger 35% radius-three discount scored 28–8 on that
screen, but the full panel finished at 71–37, two wins ahead of V54 and one
net outcome behind v02 on paired fixtures (9 better / 7 worse / 92 same vs
V54; 7 better / 8 worse / 93 same vs v02). Keep v02 as the current leader.
Runs: `experiment_data/skadi-v04-fafnir-radius2_20260927113934495373`,
`experiment_data/skadi-v05-fafnir-stronger_20260927114518104843` (screen), and
`experiment_data/skadi-v05-fafnir-stronger_20260927114924520983` (full panel).
