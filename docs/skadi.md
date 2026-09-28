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

## Fresh-seed check (2026-09-27)

The 15% Fafnir setting (v06) led on the tuning panel, so I reran it against
the same nine-family field and a Gavroche V54 direct control under new fixture
hashes. Gavroche was rerun on the exact same 120-fixture schedule. The
opponent/map/side keys and all 108 gauntlet seeds match exactly; bot-internal
random choices are not seeded by this harness, so an individual paired flip
is noisy.

| Candidate | 108-game gauntlet W–D–L | Win-equivalent points | Direct V54 | Logged runtime faults |
|---|---:|---:|---:|---:|
| Gavroche V54 | 64–1–43 | 64.5 | 6–6 self-play | 0 |
| Skadi v06, 15% support discount | 60–1–47 | 60.5 | 7–5 | 11 |
| Skadi v02, 25% support discount | 64–1–43 | 64.5 | 5–7 | 0 |

V06's gains and regressions across the nine families nearly cancel its earlier
+5 outcome lead on the tuning panel; it is not a clear upgrade. Its run logs
recorded 11 `exit code 2` events (the counter includes either team), compared
with none in V54's rerun. V02 ties V54's score on these fresh fixtures, with
nine outcome flips in each direction, and also loses the direct match. Neither
setting meets the promotion bar. Continue tuning from evidence and require a
separate fresh-seed check before promotion.

Fresh-seed reports: `experiment_data/skadi-v06-fafnir-light_20260927131000087468`,
`experiment_data/gavroche-final_20260927132417577164`, and
`experiment_data/skadi-v02-fafnir-only_20260927134036388168`. The holdout config
and renamed opponent snapshots are captured in each run's manifest and source
snapshot.

The 10% support discount (v08) also failed to pass this same 108-game check:
61–1–46, versus V54's 64–1–43, with four Skadi-only wins and seven V54-only
wins among the changed fixtures. It had no logged runtime faults and went 7–5
in direct play. Report: `experiment_data/skadi-v08-fafnir-subtle_20260928014400108327`.

V10 checks support at the candidate collision tile rather than at the enemy's
current location. This more targeted version scored 62–1–45 against V54's
64–1–43, lost the direct match 4–8, and had no logged runtime faults. It also
does not advance. Report: `experiment_data/skadi-v10-fafnir-local-reach_20260928015908174879`.

## Compact fast-bed transfer

Skadi v11 transfers Newton's 0.9 contested-bed valuation, scoped to 256–625
tiles, and uses Witten x03's consecutive-observation countdown reset to
confirm a fast bed before changing its value. On five eligible maps (100
fixtures including V54 self-play), v11 recorded 61–39 with no faults. On the
90 shared non-self-play fixtures it scored 57–33, compared with V54's 63–27;
paired changes favored V54 10 to 4. The largest regression was Colosseum
(8–10 vs 12–6); devil and dilemma tied. Do not carry this transfer forward.

Reports: `experiment_data/skadi-v11-fastbed-contest_20260928024337464845` and
`experiment_data/gavroche-final_20260928024647982271`.

## Portal-exit memory

The third fresh-seed run of Fafnir-only v02 scored 69–39 against V54's 71–37
on the shared 108 fixtures. Paired results changed in Skadi's favor on 9 games
and V54's favor on 11; direct play was 8–4 for Skadi. This confirms the earlier
Fafnir settings do not yet establish an upgrade. Reports:
`experiment_data/skadi-v02-fafnir-only_20260928021340369904` and
`experiment_data/gavroche-final_20260928022626382617`.

Skadi v12 transfers Witten x01's recent-body and recent-visibility memory to
estimate risk at hidden portal exits. On a five-map screen, it scored 67–23 on
90 shared non-self fixtures versus V54's 59–31; 18 outcomes changed for Skadi
and 10 for V54. On the standard six-map panel, it scored 76–32 versus V54's
69–39, with 11 paired outcomes better and 4 worse. But on a fresh renamed-
opponent holdout it tied V54 at 67–41, with 11 changed outcomes in each
direction. Direct V54 play was 6–4 on the first screen and 7–5 on each standard
panel. The standard-panel edge did not repeat, so v12 is not a confirmed
upgrade.

V12's four judge-sandbox games on Big Empty and Trauma had p99 CPU of
43.4–44.1M points, maximum 60.2M, and no TLEs or runtime faults. Skadi v13
keeps V54's full risk for unseen exits and discounts risk only when an exit was
recently seen clear. Its standard panel scored 71–37 on the shared fixtures
versus V54's 69–39; paired results favored Skadi 8 to 6, and direct play was
8–4. This is below the +4 net promotion gate and has not had a fresh holdout or
CPU screen. Neither portal variant advances; Gavroche V54 remains the best
supported Gavroche/Skadi baseline. The v13 holdout was not run, following the
request to stop after this iteration.

V12 reports: `experiment_data/skadi-v12-portal-exit-memory_20260928025251864461`,
`experiment_data/gavroche-final_20260928030120071926`,
`experiment_data/skadi-v12-portal-exit-memory_20260928031751088940`,
`experiment_data/gavroche-final_20260928032911316538`,
`experiment_data/skadi-v12-portal-exit-memory_20260928034047435985`,
`experiment_data/gavroche-final_20260928035452736665`, and CPU report
`experiment_data/skadi-v12-portal-exit-memory_20260928031021779587`. V13 report:
`experiment_data/skadi-v13-clear-exit-only_20260928040905425814`.
