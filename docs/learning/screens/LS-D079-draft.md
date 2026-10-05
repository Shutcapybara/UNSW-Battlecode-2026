# LS-D079 — paired live screen, DRAFT (prepared under D-079; not dispatched)

Prepared 2026-10-05 ~10:00Z by daichi. Dispatch only on a later Chair D-record.

## Job body (battles.json; `expect_active` is set by the hub at acceptance)

```json
{"label": "LS-D079", "by": "daichi", "decision": "D-0xx (dispatch record)",
 "note": "D-079 paired live screen: 17530 bokuto-13-cull and 17388 kenma-03-pocket-queen vs ref 14585 carthage-05",
 "arms": [{"submission": 14585}, {"submission": 17530}, {"submission": 17388}],
 "opponents": [347, 187, 959, 1091, 507, 213],
 "seats": "both", "games_per_pair": 2, "max_games": 360, "deadline_hours": 20}
```

Maps omitted = every active map (17); 20 games per arm per opponent ≈ 10 maps × 2 seats per pass.

## Roster (ladder snapshot 09:46Z; we are 1749, rank 82)

| band | team | Elo | rank | games in corpus since 4 Oct 10Z |
|---|---|---|---|---|
| near us | 347 | 1742 | 85 | 738 (LS-1 opponent, accepted requests) |
| near us | 187 | 1762 | 78 | 488 |
| near 1900 | 959 | 1907 | 45 | 480 |
| near 1900 | 1091 | 1901 | 47 | 416 |
| top ten | 507 | 2213 | 9 | 927 |
| top ten | 213 | 2233 | 7 | 704 |

Excluded: dev teams; 1022 and 989 (names match programme bot series; possible related teams).

## Size (simulation, `sz.py`: pair diff ∈ {−1,0,+1}, non-zero share 0.39 and pair SD 0.62 from LS-1's 80 pairs;
## 6 opponent clusters; cluster bootstrap 5th/95th, 400 B; true difference +0.10; τ = between-opponent SD of the effect)

| pairs / opponent | pairs per comparison | games (3 arms) | P(5th pct > 0), τ 0 | τ 0.08 | half-width τ 0 / 0.08 |
|---|---|---|---|---|---|
| 10 | 60 | 180 | 0.43 | 0.40 | 0.111 / 0.121 |
| 20 | 120 | 360 | 0.57 | 0.48 | 0.080 / 0.092 |
| 30 | 180 | 540 | 0.71 | 0.60 | 0.063 / 0.078 |
| 40 | 240 | 720 | 0.82 | 0.65 | 0.057 / 0.073 |
| 60 | 360 | 1080 | 0.94 | 0.72 | 0.046 / 0.065 |

A 6-cluster bootstrap is anti-conservative (true coverage below nominal); read the half-widths as lower bounds.
**A paired difference of 0.10 needs ~240 pairs per comparison (720 games) for 0.8 power if the effect is the same on
every opponent; with opponent heterogeneity it does not reach 0.8 below ~1,000 games.** 360 games resolves ±0.08–0.09.

## Field allowance

hourly_games.field 60, executor_cap.field 45, reserve shared with the collector; LS-1 achieved ~20 games/h
(160 games, 4 Oct 17:42Z→02:15Z incl. an outage). 360 games ≈ 10–18 h; 720 ≈ 20–36 h. "Same hour" holds within a unit
(all three arms back to back, arm order shuffled), not across the screen.

## Can an inactive submission play while another holds the live slot?

Not directly: POST /api/v1/battles takes teamId, ranked, mapIds only and plays the team's active submission. The hub does
it by temporary activation (executor.request_batch: reserve → activate arm → POST → restore), for the seconds of each
POST, never in the even-hour blackout and never while one of our ranked series is in flight. LS-1 played 80 games of
inactive 16979 this way, 0 runtime faults, 0 lost restores. Risk during a trial window: a ranked series that starts
inside a switch would be played by the wrong arm and enter the trial window — dispatch after the look, or exclude any
ranked game started within a switch from the trial statistic.
