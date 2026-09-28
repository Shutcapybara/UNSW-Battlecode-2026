# Heimdall family

Heimdall is a Bifröst/Fenrir-derived family with selective ideas from Loki and
Skadi. The leading candidate keeps Fenrir v18's newborn handoff and child-site
separation, Bifröst's portal-exit memory, and uses `world.echo` for two distinct
signals: aggregate enemy activity and isolated directional scans.

## Echo handling

The observation's echo is a five-count aggregate for the previous turn's rays:
kelp, ally, ally head, enemy, enemy head. The aggregate alone has no direction
or coordinate. Heimdall v05 uses enemy counts as a broad activity signal: it
shortens the bed wait horizon after contact and slightly scales visible
head-threat costs.

Heimdall v10 adds an isolated scan every fourth action when no critical radio
packet is queued. It sends one ray and remembers its post-action origin and
absolute direction. On the next turn, a nonzero enemy count can then be
associated with that ray, and the movement scorer gives recently echoed lanes a
small, decaying cost. Since the scan is isolated, no location is inferred from
an aggregate of multiple rays. Crown, prey, legacy handoff, and Fenrir `T_SPLIT`
packets keep priority; the scan only replaces lower-priority radio traffic.

## Iteration record

The core screen uses nine maps, both seats, and 18 games against each of
Bifröst v01 and Fenrir v18. All completed core screens had zero game errors.
The performance moved materially with bed timing, so those candidates were
kept separate rather than combining their settings:

| Candidate | Change | vs Bifröst | vs Fenrir |
|---|---|---:|---:|
| [v01 echo lane](../bots/heimdall-v01-echo-lane/README.md) | Initial isolated scan prototype; abandoned after split-handoff traffic was not protected | Incomplete; no wins in completed fixtures | Incomplete; no wins in completed fixtures |
| [v02 echo risk](../bots/heimdall-v02-echo-risk/README.md) | Aggregate echo risk with Bifröst-style bed timing | 10–8 in partial screen | 5–13 in partial screen |
| [v03 local echo threat](../bots/heimdall-v03-local-echo-threat/README.md) | Fenrir timing plus modest echo-scaled visible threat | 8–9–1 | 9–9 |
| [v04 arrival bed window](../bots/heimdall-v04-arrival-bed-window/README.md) | Fixed 12-round bed horizon | 11–7 | 6–12 |
| [v05 echo-conditioned beds](../bots/heimdall-v05-echo-conditioned-beds/README.md) | Up to 12 rounds, shortened by enemy echo activity | 12–6 | 7–11 |
| [v06 head-echo bed switch](../bots/heimdall-v06-head-echo-bed-switch/README.md) | Set bed wait to zero on any enemy-head echo | 9–9 | 6–12 |
| [v07 size-matched support](../bots/heimdall-v07-size-matched-support/README.md) | Add Skadi v02's size-matched counter-threat support | 8–10 | 7–11 |
| [v08 teacher tie-break](../bots/heimdall-v08-teacher-tiebreak/README.md) | Add Loki's trained candidate ranker at low scale | 11–7 | 7–11 |
| [v09 short bed window](../bots/heimdall-v09-short-echo-bed-window/README.md) | Halve v05's maximum echo-conditioned bed horizon | 9–9 | 8–10 |
| [v10 isolated echo lanes](../bots/heimdall-v10-isolated-echo-lanes/README.md) | Add isolated scans to v05 and preserve split handoffs | **12–6** | **11–7** |

The v01 scan prototype's `_critical()` omitted `T_SPLIT`, allowing scheduled
scans to replace child handoff messages. V10 protects that packet type. The
Loki model in v08 did not help against Fenrir and lost the v05 Big Empty gains;
it is not included in v10. The Skadi support transfer in v07 also did not
improve the core panel.

## Champion panel

V10 completed the full 15-map, both-seat panel: 30 games per reference, 150
games total, with no game errors, analysis errors, or reported runtime faults.

| Reference | Heimdall W–L | Score |
|---|---:|---:|
| Bifröst v01 portal memory | 20–10 | 66.7% |
| Fenrir v18 arrival-ready beds | 16–14 | 53.3% |
| Loki v01 teacher ranker | 19–11 | 63.3% |
| Skadi v02 Fafnir-only | 17–13 | 56.7% |
| Skadi v13 clear-exit-only | 19–11 | 63.3% |
| **Total** | **91–59** | **60.7%** |

The expanded panel identifies remaining weak maps: V10 went 0–2 against Fenrir
on Colosseum, Default, Queen of Spades, Schooltime, and Stronghold, and went 0–2
against Bifröst on Portals. It still finished above 50% against each reference
on the complete fixture.

Full report: [`experiment_data/heimdall-v10-isolated-echo-lanes_20260928073239050343`](../experiment_data/heimdall-v10-isolated-echo-lanes_20260928073239050343/summary.md). The earlier five-reference screen is at [`experiment_data/heimdall-v10-isolated-echo-lanes_20260928072233772956`](../experiment_data/heimdall-v10-isolated-echo-lanes_20260928072233772956/summary.md).

## Runtime check and limits

One Big Empty game against Fenrir v18 completed in the official judge sandbox
for all 500 rounds. Heimdall used 49.6M p99 and 57.8M maximum CPU points, with
no runtime fault. This is a focused CPU check, not a full sandbox panel.

The comparison runner uses fixture-hash seeds, but bot-internal random streams
are not fully controlled. The results are one 15-map fixture panel and should
be treated as a broad measured advantage on that panel, not a guarantee across
all random bot behavior or future opponents.
