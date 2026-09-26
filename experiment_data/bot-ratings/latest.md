# Current bot estimates

Updated 2026-09-26T04:09:55.426470+00:00; ledger snapshot taken 2026-09-26T04:09:20.690508+00:00.

236 frozen bot versions, 13 maps, 57,067 distinct fixtures from 57,920 matching records in the 64,063-game shared ledger.

Score is predicted win + half-draw rate against the same reference panel, equally weighting maps and starting sides. The model adjusts for opponent, map and side, and uses matchup interactions when held-out prediction improves. Ranges show the middle 80% of opponent-pair bootstrap estimates, expanded to include the point estimate; they are sensitivity ranges, not calibrated confidence intervals.

Sparse means fewer than 60 fixtures, 5 opponents or 8 maps. Similarity means the smallest observed score difference on at least 30 shared paired opponent/map cells; it does not establish similar code or tactics. Missing games and errors are excluded.

| Rank | Bot | Score | Range | Fixtures | Opponents | Maps | Evidence | Closest observed profile |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | vn-x06-info-grad1 | 84.0% | 77.6%–87.4% | 36 | 8 | 10 | Sparse | Insufficient overlap |
| 2 | sinbad-v07-divecap | 84.0% | 76.0%–90.1% | 114 | 55 | 13 | Established | Insufficient overlap |
| 3 | von_neumann-x04-support | 83.1% | 77.4%–86.5% | 87 | 29 | 13 | Established | Insufficient overlap |
| 4 | von_neumann-x06-info | 81.4% | 76.1%–85.0% | 46 | 7 | 9 | Sparse | Insufficient overlap |
| 5 | von_neumann-x03-balance | 80.8% | 73.3%–82.4% | 82 | 28 | 13 | Established | Insufficient overlap |
| 6 | vn-x01-atkunits-1 | 79.2% | 71.6%–80.9% | 80 | 25 | 13 | Established | Insufficient overlap |
| 7 | feynman-x01-frozen | 78.9% | 68.7%–88.6% | 14 | 7 | 7 | Sparse | Insufficient overlap |
| 8 | von_neumann-x02-mech | 78.4% | 69.2%–80.6% | 84 | 27 | 13 | Established | Insufficient overlap |
| 9 | von_neumann-x01-frozen | 78.3% | 70.0%–79.5% | 78 | 27 | 13 | Established | Insufficient overlap |
| 10 | valjean-v01-portal-memory | 77.7% | 67.3%–81.6% | 86 | 35 | 13 | Established | Insufficient overlap |
| 11 | vn-x01-preymin-6 | 77.2% | 72.2%–79.2% | 78 | 28 | 13 | Established | Insufficient overlap |
| 12 | godel-x12-tb25-margin1 | 76.9% | 70.8%–78.9% | 26 | 4 | 5 | Sparse | Insufficient overlap |
| 13 | godel-x18-ps3-030 | 76.9% | 65.3%–81.0% | 26 | 4 | 5 | Sparse | Insufficient overlap |
| 14 | godel-x07-tradebias25 | 76.7% | 73.0%–78.1% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 15 | godel-x15-tb25-gs4 | 76.6% | 74.1%–76.6% | 26 | 4 | 5 | Sparse | Insufficient overlap |
| 16 | godel-x13-tb25-au4 | 76.4% | 73.9%–77.7% | 26 | 4 | 5 | Sparse | Insufficient overlap |
| 17 | vn-x01-sat-09 | 76.3% | 71.7%–78.2% | 78 | 27 | 13 | Established | Insufficient overlap |
| 18 | godel-x14-tb25-ps2-05 | 75.7% | 69.2%–77.7% | 40 | 11 | 11 | Sparse | Insufficient overlap |
| 19 | monte_christo-x12-remote-density | 75.7% | 70.3%–80.4% | 164 | 54 | 13 | Established | monte_christo-x04-channel-only (25.0 pp gap; 36 cells) |
| 20 | vn-x01-margin-2 | 75.1% | 70.4%–78.3% | 78 | 30 | 13 | Established | Insufficient overlap |
| 21 | athos-x06-f-crown | 75.0% | 72.4%–78.6% | 176 | 56 | 13 | Established | athos-x17-f-crownsafe (4.4 pp gap; 45 cells) |
| 22 | tew-v10-supported-hunts | 74.7% | 73.8%–77.9% | 378 | 33 | 13 | Established | tew-v12-mid-support (1.4 pp gap; 146 cells) |
| 23 | porthos-x04-policy | 74.5% | 71.6%–76.5% | 378 | 45 | 13 | Established | porthos-x03-swarm (13.7 pp gap; 91 cells) |
| 24 | athos-x13-c-all-menu | 74.3% | 68.3%–76.4% | 150 | 40 | 13 | Established | athos-x11-c-all (0.0 pp gap; 46 cells) |
| 25 | tew-v07-production-ladder | 74.1% | 71.7%–76.0% | 422 | 37 | 13 | Established | ouroboros-v13-ladder (0.0 pp gap; 50 cells) |
| 26 | godel-x11-tradebias35 | 74.1% | 62.3%–78.2% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 27 | godel-x17-ps2-065 | 74.0% | 58.5%–76.3% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 28 | athos-x15-f-allyreach | 73.6% | 70.0%–77.0% | 154 | 45 | 13 | Established | athos-x18-f-latesplit (10.2 pp gap; 44 cells) |
| 29 | ouroboros-v13-ladder | 73.5% | 68.4%–76.7% | 1428 | 130 | 13 | Established | tew-v07-production-ladder (0.0 pp gap; 50 cells) |
| 30 | aramis-x01-extracted | 73.4% | 69.3%–77.2% | 146 | 63 | 13 | Established | Insufficient overlap |
| 31 | monte_christo-x13-priority-channel | 73.4% | 70.5%–76.1% | 136 | 40 | 13 | Established | monte_christo-v01-core (15.0 pp gap; 30 cells) |
| 32 | monte_christo-x04-channel-only | 73.4% | 69.5%–77.7% | 142 | 27 | 13 | Established | porthos-x03-swarm (8.1 pp gap; 37 cells) |
| 33 | monte_christo-x02-density-h12 | 73.3% | 65.3%–76.6% | 86 | 31 | 13 | Established | Insufficient overlap |
| 34 | avery-v09-frontier-bfs | 73.3% | 64.2%–78.9% | 220 | 50 | 13 | Established | tew-v09-low-gate (9.7 pp gap; 31 cells) |
| 35 | athos-x11-c-all | 73.2% | 69.7%–76.9% | 148 | 39 | 13 | Established | athos-x13-c-all-menu (0.0 pp gap; 46 cells) |
| 36 | athos-x18-f-latesplit | 73.2% | 67.1%–74.6% | 148 | 42 | 13 | Established | athos-v01-core (0.0 pp gap; 43 cells) |
| 37 | godel-x05-margin1 | 73.2% | 63.8%–76.3% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 38 | godel-x10-crownkill340 | 73.2% | 67.7%–76.7% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 39 | godel-x09-midhunt55 | 73.1% | 52.3%–82.8% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 40 | godel-x04-attackunits4 | 73.1% | 62.3%–80.7% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 41 | athos-x14-e-splitn | 73.1% | 68.9%–74.5% | 148 | 42 | 13 | Established | athos-x12-menu-strict (1.2 pp gap; 41 cells) |
| 42 | monte_christo-v03-logistic-risk | 73.0% | 69.2%–73.8% | 176 | 39 | 13 | Established | monte_christo-v04-supported-risk (10.4 pp gap; 48 cells) |
| 43 | godel-x20-inc-margin1 | 72.9% | 65.7%–78.7% | 26 | 4 | 5 | Sparse | Insufficient overlap |
| 44 | tew-v09-low-gate | 72.9% | 71.8%–74.6% | 362 | 32 | 13 | Established | ouroboros-v13-ladder (0.0 pp gap; 43 cells) |
| 45 | tew-v08-early-hunter | 72.8% | 71.5%–75.1% | 382 | 29 | 13 | Established | tew-v10-supported-hunts (2.7 pp gap; 147 cells) |
| 46 | monte_christo-v06-density | 72.7% | 63.6%–76.7% | 136 | 24 | 13 | Established | monte_christo-x11-crown-priority (14.9 pp gap; 37 cells) |
| 47 | athos-x01-e-trapmargin | 72.5% | 68.2%–74.8% | 144 | 40 | 13 | Established | athos-x13-c-all-menu (6.5 pp gap; 46 cells) |
| 48 | sinbad-v03-hunt | 72.5% | 64.9%–75.9% | 576 | 59 | 13 | Established | monte_christo-v01-core (3.0 pp gap; 132 cells) |
| 49 | tew-v11-close-support | 72.3% | 70.8%–75.9% | 350 | 29 | 13 | Established | tew-v07-production-ladder (3.0 pp gap; 148 cells) |
| 50 | aramis-x09-frontier | 72.2% | 63.7%–76.7% | 140 | 62 | 13 | Established | Insufficient overlap |
| 51 | monte_christo-v05-compact-risk | 72.2% | 65.2%–77.0% | 112 | 56 | 13 | Established | Insufficient overlap |
| 52 | avery-v07-compact-production | 72.2% | 69.9%–78.3% | 240 | 38 | 13 | Established | avery-v06-late-feed (4.7 pp gap; 86 cells) |
| 53 | athos-v01-core | 72.1% | 67.6%–75.2% | 150 | 37 | 13 | Established | athos-x18-f-latesplit (0.0 pp gap; 43 cells) |
| 54 | athos-x04-f-splitval | 72.1% | 69.8%–75.8% | 142 | 39 | 13 | Established | athos-x12-menu-strict (4.9 pp gap; 41 cells) |
| 55 | avery-v12-hungry-sweep | 72.1% | 63.9%–80.6% | 42 | 21 | 12 | Sparse | Insufficient overlap |
| 56 | sinbad-v05-hunt8 | 72.0% | 60.1%–76.5% | 144 | 70 | 13 | Established | Insufficient overlap |
| 57 | tew-v12-mid-support | 72.0% | 71.0%–74.0% | 3410 | 203 | 13 | Established | tew-v10-supported-hunts (1.4 pp gap; 146 cells) |
| 58 | athos-x17-f-crownsafe | 71.9% | 69.2%–74.7% | 152 | 44 | 13 | Established | athos-x06-f-crown (4.4 pp gap; 45 cells) |
| 59 | athos-x12-menu-strict | 71.9% | 67.5%–73.6% | 140 | 38 | 13 | Established | athos-x14-e-splitn (1.2 pp gap; 41 cells) |
| 60 | godel-x01-frozen | 71.9% | 66.2%–75.9% | 74 | 27 | 13 | Established | Insufficient overlap |
| 61 | avery-v08-crown-race | 71.8% | 67.2%–73.7% | 326 | 33 | 13 | Established | avery-v07-compact-production (5.7 pp gap; 87 cells) |
| 62 | monte_christo-v02-table-risk | 71.6% | 68.4%–74.6% | 156 | 29 | 13 | Established | monte_christo-v01-core (10.6 pp gap; 47 cells) |
| 63 | athos-x03-e-sprintpearl | 71.4% | 66.3%–75.0% | 132 | 34 | 13 | Established | athos-x12-menu-strict (15.6 pp gap; 45 cells) |
| 64 | monte_christo-v04-supported-risk | 70.8% | 65.0%–73.2% | 194 | 26 | 13 | Established | monte_christo-v03-logistic-risk (10.4 pp gap; 48 cells) |
| 65 | godel-x19-ps1-090 | 70.7% | 61.2%–76.4% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 66 | javert-x02-lendensity | 70.6% | 66.5%–79.2% | 72 | 28 | 13 | Established | Insufficient overlap |
| 67 | porthos-x03-swarm | 70.4% | 67.4%–73.7% | 182 | 7 | 13 | Established | monte_christo-x04-channel-only (8.1 pp gap; 37 cells) |
| 68 | monte_christo-x10-sparse-radio | 70.2% | 66.5%–75.5% | 122 | 49 | 13 | Established | Insufficient overlap |
| 69 | godel-x08-pstrike06 | 70.1% | 54.7%–74.1% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 70 | godel-x16-ps2only | 70.0% | 55.5%–75.4% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 71 | athos-x08-c-trap-split | 69.9% | 66.5%–75.2% | 106 | 41 | 13 | Established | Insufficient overlap |
| 72 | godel-x03-berserk | 69.8% | 66.2%–76.1% | 86 | 33 | 13 | Established | Insufficient overlap |
| 73 | athos-x09-c-trap-crown | 69.8% | 65.7%–72.6% | 130 | 53 | 13 | Established | Insufficient overlap |
| 74 | porthos-x05-recon | 69.6% | 65.7%–73.1% | 182 | 7 | 13 | Established | porthos-x03-swarm (8.8 pp gap; 91 cells) |
| 75 | monte_christo-v07-radio | 69.4% | 66.8%–75.0% | 120 | 39 | 13 | Established | Insufficient overlap |
| 76 | porthos-x02-intentions | 69.4% | 63.6%–70.3% | 274 | 41 | 13 | Established | monte_christo-v01-core (0.0 pp gap; 113 cells) |
| 77 | athos-x10-c-split-crown | 69.2% | 59.5%–74.2% | 116 | 46 | 13 | Established | Insufficient overlap |
| 78 | monte_christo-v01-core | 68.7% | 64.1%–71.7% | 715 | 70 | 13 | Established | porthos-x02-intentions (0.0 pp gap; 113 cells) |
| 79 | javert-x05-space | 68.7% | 62.8%–70.9% | 56 | 20 | 12 | Sparse | Insufficient overlap |
| 80 | monte_christo-x08-no-relay | 68.6% | 59.8%–72.1% | 32 | 4 | 4 | Sparse | Insufficient overlap |
| 81 | athos-x07-f-menu-feed | 68.5% | 65.7%–72.2% | 118 | 47 | 13 | Established | Insufficient overlap |
| 82 | monte_christo-x06-control-gradient | 68.2% | 64.7%–72.5% | 112 | 44 | 13 | Established | Insufficient overlap |
| 83 | sinbad-v02-crown | 67.8% | 66.1%–71.4% | 142 | 31 | 13 | Established | monte_christo-v03-logistic-risk (20.0 pp gap; 30 cells) |
| 84 | aramis-x07-preview-policy | 67.8% | 62.1%–72.4% | 94 | 41 | 13 | Established | Insufficient overlap |
| 85 | monte_christo-x07-all-density | 67.5% | 55.4%–71.1% | 44 | 10 | 10 | Sparse | Insufficient overlap |
| 86 | tew-v14-strict-crown | 67.3% | 63.4%–70.2% | 159 | 36 | 13 | Established | tew-v10-supported-hunts (11.5 pp gap; 48 cells) |
| 87 | monte_christo-x09-fast-observe | 67.2% | 60.1%–72.5% | 102 | 39 | 13 | Established | Insufficient overlap |
| 88 | tew-v15-crown-banking | 67.2% | 62.3%–72.0% | 155 | 34 | 13 | Established | tew-v16-compact-crown-bank (4.5 pp gap; 33 cells) |
| 89 | tew-v18-open-trade-gate | 67.1% | 62.3%–72.3% | 104 | 43 | 13 | Established | Insufficient overlap |
| 90 | avery-v11-maze-sweep | 67.0% | 65.2%–69.8% | 176 | 16 | 13 | Established | ouroboros-v10-beacon (11.6 pp gap; 56 cells) |
| 91 | godel-x06-strikebonus2 | 66.8% | 58.1%–73.8% | 24 | 3 | 4 | Sparse | Insufficient overlap |
| 92 | avery-v06-late-feed | 66.5% | 58.1%–69.9% | 384 | 25 | 13 | Established | avery-v07-compact-production (4.7 pp gap; 86 cells) |
| 93 | dartegnan-x01-e0p0 | 65.9% | 61.7%–74.2% | 76 | 29 | 13 | Established | Insufficient overlap |
| 94 | javert-x04-portals | 65.8% | 60.7%–69.5% | 64 | 24 | 12 | Established | Insufficient overlap |
| 95 | sinbad-v04-strike | 65.8% | 60.4%–79.2% | 152 | 75 | 13 | Established | Insufficient overlap |
| 96 | javert-x03-policy | 65.6% | 60.7%–71.2% | 52 | 18 | 12 | Sparse | Insufficient overlap |
| 97 | monte_christo-x01-density-h1 | 65.5% | 60.0%–70.0% | 86 | 31 | 13 | Established | Insufficient overlap |
| 98 | monte_christo-x11-crown-priority | 65.4% | 63.6%–73.9% | 106 | 25 | 13 | Established | monte_christo-v06-density (14.9 pp gap; 37 cells) |
| 99 | athos-x02-e-headblock | 65.4% | 61.7%–71.6% | 118 | 47 | 13 | Established | Insufficient overlap |
| 100 | javert-v01-game-relative | 65.4% | 63.3%–74.1% | 82 | 41 | 13 | Established | Insufficient overlap |
| 101 | leviathan-v09-arrival | 65.3% | 62.7%–67.9% | 999 | 94 | 13 | Established | ouroboros-v11-opening (8.9 pp gap; 109 cells) |
| 102 | sinbad-v06-arrival | 65.3% | 59.2%–76.4% | 66 | 21 | 12 | Established | Insufficient overlap |
| 103 | avery-v03-swarm-spacing | 65.1% | 61.4%–67.1% | 258 | 17 | 13 | Established | avery-v05-strict-crown (6.9 pp gap; 108 cells) |
| 104 | tew-v13-compact-survival | 65.1% | 63.9%–68.6% | 144 | 22 | 13 | Established | tew-v17-balanced-compact-growth (0.0 pp gap; 34 cells) |
| 105 | tew-v17-balanced-compact-growth | 64.6% | 59.4%–65.7% | 230 | 21 | 13 | Established | tew-v13-compact-survival (0.0 pp gap; 34 cells) |
| 106 | tew-v16-compact-crown-bank | 64.3% | 61.3%–68.3% | 130 | 20 | 13 | Established | tew-v15-crown-banking (4.5 pp gap; 33 cells) |
| 107 | sinbad-v01-core | 63.9% | 59.2%–66.5% | 116 | 19 | 13 | Established | tew-v15-crown-banking (17.2 pp gap; 32 cells) |
| 108 | aramis-v01-intentions | 63.9% | 57.3%–72.7% | 116 | 35 | 13 | Established | monte_christo-v01-core (29.8 pp gap; 31 cells) |
| 109 | aramis-x02-intentions | 63.9% | 58.0%–67.8% | 82 | 35 | 13 | Established | Insufficient overlap |
| 110 | porthos-x01-frozen | 63.8% | 56.1%–69.9% | 136 | 67 | 13 | Established | Insufficient overlap |
| 111 | monte_christo-x05-period-four | 63.6% | 59.7%–71.5% | 72 | 24 | 13 | Established | Insufficient overlap |
| 112 | hunter-v23-supported-arrival-feed | 62.7% | 52.5%–73.4% | 70 | 34 | 13 | Established | Insufficient overlap |
| 113 | aramis-v02-frontier | 62.5% | 57.5%–72.1% | 148 | 62 | 13 | Established | Insufficient overlap |
| 114 | avery-v05-strict-crown | 62.5% | 58.5%–63.8% | 2600 | 125 | 13 | Established | avery-v03-swarm-spacing (6.9 pp gap; 108 cells) |
| 115 | monte_christo-x03-local-density | 61.8% | 58.6%–67.1% | 90 | 33 | 13 | Established | Insufficient overlap |
| 116 | leviathan-x03-estuary-roles | 61.4% | 60.2%–63.8% | 951 | 93 | 13 | Established | avery-v08-crown-race (16.7 pp gap; 51 cells) |
| 117 | dartegnan-x03-e1p0 | 60.6% | 55.4%–65.7% | 60 | 21 | 13 | Established | Insufficient overlap |
| 118 | aramis-x03-e0f0 | 59.7% | 54.9%–71.0% | 84 | 36 | 13 | Established | Insufficient overlap |
| 119 | avery-v10-safe-explore | 59.2% | 54.7%–67.8% | 142 | 71 | 13 | Established | Insufficient overlap |
| 120 | avery-v02-id-order-corridors | 59.0% | 56.9%–60.8% | 190 | 13 | 13 | Established | avery-v04-crown-endgame (18.1 pp gap; 83 cells) |
| 121 | avery-v04-crown-endgame | 58.7% | 57.8%–61.0% | 298 | 17 | 13 | Established | avery-v05-strict-crown (12.9 pp gap; 132 cells) |
| 122 | aramis-x06-e1f1 | 58.4% | 52.5%–63.3% | 66 | 27 | 13 | Established | Insufficient overlap |
| 123 | dartegnan-v01-contract | 58.4% | 49.8%–66.5% | 53 | 18 | 12 | Sparse | Insufficient overlap |
| 124 | godel-x02-pacifist | 58.2% | 52.5%–64.7% | 52 | 17 | 13 | Sparse | Insufficient overlap |
| 125 | aramis-x04-e0f1 | 57.1% | 51.5%–62.4% | 70 | 29 | 13 | Established | Insufficient overlap |
| 126 | leviathan-v08-core | 57.0% | 55.8%–59.1% | 992 | 94 | 13 | Established | ouroboros-v10-beacon (0.0 pp gap; 203 cells) |
| 127 | ouroboros-v12-core | 56.8% | 54.3%–60.3% | 930 | 84 | 13 | Established | leviathan-v08-core (0.0 pp gap; 100 cells) |
| 128 | ouroboros-v11-opening | 56.6% | 54.8%–60.0% | 969 | 87 | 13 | Established | leviathan-v08-core (0.0 pp gap; 107 cells) |
| 129 | athos-x05-f-threat | 55.3% | 50.2%–62.1% | 74 | 25 | 13 | Established | Insufficient overlap |
| 130 | ouroboros-v09-feed | 54.2% | 51.2%–56.8% | 967 | 83 | 13 | Established | ouroboros-v12-core (5.1 pp gap; 88 cells) |
| 131 | dartegnan-x05-e0p2 | 54.2% | 52.8%–60.0% | 56 | 20 | 12 | Sparse | Insufficient overlap |
| 132 | hunter-v15-shared-territory | 53.5% | 52.0%–56.1% | 960 | 83 | 13 | Established | hunter-v17-portal-first-traps (1.5 pp gap; 103 cells) |
| 133 | hunter-v18-self-trap-lookahead | 53.5% | 49.3%–54.7% | 937 | 83 | 13 | Established | hunter-v19-safe-growth-lookahead (4.3 pp gap; 105 cells) |
| 134 | aramis-x05-e1f0 | 53.4% | 47.2%–57.7% | 70 | 29 | 13 | Established | Insufficient overlap |
| 135 | ouroboros-v02-crown | 53.2% | 51.1%–55.4% | 909 | 85 | 13 | Established | ouroboros-v01-eval (10.3 pp gap; 87 cells) |
| 136 | ouroboros-v03-forage | 53.1% | 49.9%–54.1% | 973 | 86 | 13 | Established | formatted-hunter-v22 (17.5 pp gap; 40 cells) |
| 137 | avery-v01-safe-swarm | 52.9% | 50.5%–54.3% | 212 | 24 | 13 | Established | drake-v07-soft-missions (16.7 pp gap; 63 cells) |
| 138 | chimera-v01-unified | 52.9% | 52.2%–64.2% | 134 | 67 | 13 | Established | Insufficient overlap |
| 139 | ouroboros-v10-beacon | 52.8% | 51.5%–55.6% | 2708 | 144 | 13 | Established | leviathan-v08-core (0.0 pp gap; 203 cells) |
| 140 | ouroboros-v04-race | 52.6% | 51.0%–55.4% | 962 | 89 | 13 | Established | ouroboros-v02-crown (13.3 pp gap; 83 cells) |
| 141 | hunter-v19-safe-growth-lookahead | 52.6% | 49.7%–56.4% | 963 | 83 | 13 | Established | hunter-v18-self-trap-lookahead (4.3 pp gap; 105 cells) |
| 142 | dartegnan-x04-e1p1 | 52.6% | 42.0%–56.8% | 54 | 19 | 11 | Sparse | Insufficient overlap |
| 143 | ouroboros-v01-eval | 52.2% | 49.1%–54.2% | 958 | 84 | 13 | Established | ouroboros-v02-crown (10.3 pp gap; 87 cells) |
| 144 | hunter-v17-portal-first-traps | 52.1% | 50.1%–53.3% | 937 | 84 | 13 | Established | hunter-v16-boost-traps (0.0 pp gap; 85 cells) |
| 145 | dartegnan-x02-e0p1 | 51.7% | 42.7%–56.2% | 54 | 19 | 12 | Sparse | Insufficient overlap |
| 146 | javert-x01-base | 50.7% | 44.4%–59.9% | 52 | 17 | 13 | Sparse | Insufficient overlap |
| 147 | ouroboros-v06-lanchester | 50.6% | 47.7%–53.4% | 939 | 87 | 13 | Established | ouroboros-v05-spread (14.1 pp gap; 92 cells) |
| 148 | ouroboros-v05-spread | 50.4% | 47.9%–52.2% | 964 | 88 | 13 | Established | drake-v10-dual-ewma (13.3 pp gap; 45 cells) |
| 149 | ouroboros-v07-forage2 | 50.3% | 47.0%–53.6% | 978 | 85 | 13 | Established | ouroboros-v08-contest (11.9 pp gap; 109 cells) |
| 150 | drake-v07-soft-missions | 50.2% | 49.9%–53.0% | 282 | 19 | 13 | Established | drake-v03-compact-production (5.4 pp gap; 121 cells) |
| 151 | aramis-x08-density-control | 50.0% | 44.8%–55.6% | 66 | 24 | 13 | Established | Insufficient overlap |
| 152 | ouroboros-v08-contest | 50.0% | 48.8%–52.7% | 976 | 89 | 13 | Established | ouroboros-v09-feed (5.7 pp gap; 88 cells) |
| 153 | hunter-v20-portal-scouts | 49.2% | 46.8%–54.0% | 3363 | 212 | 13 | Established | hunter-v21-emergency-portals (5.0 pp gap; 189 cells) |
| 154 | drake-v04-beacon | 49.0% | 47.4%–52.0% | 296 | 16 | 13 | Established | drake-v06-frontier-push (2.7 pp gap; 110 cells) |
| 155 | hunter-v22-frontier-exploration | 48.8% | 46.5%–50.4% | 908 | 83 | 13 | Established | formatted-hunter-v22 (0.0 pp gap; 32 cells) |
| 156 | hunter-v16-boost-traps | 48.6% | 47.2%–50.5% | 959 | 84 | 13 | Established | hunter-v17-portal-first-traps (0.0 pp gap; 85 cells) |
| 157 | aramis-x10-withdraw | 48.5% | 40.2%–57.9% | 70 | 27 | 13 | Established | Insufficient overlap |
| 158 | drake-v11-satutfix | 48.1% | 45.0%–55.0% | 104 | 34 | 13 | Established | hunter-v20-portal-scouts (32.2 pp gap; 45 cells) |
| 159 | drake-v06-frontier-push | 47.7% | 46.5%–49.2% | 238 | 16 | 13 | Established | drake-v04-beacon (2.7 pp gap; 110 cells) |
| 160 | hunter-v13-hybrid-route-spacing | 47.6% | 43.4%–50.3% | 960 | 83 | 13 | Established | hunter-v14-cpp-hybrid-route-spacing (4.5 pp gap; 100 cells) |
| 161 | hunter-v12-static-map-spacing | 47.6% | 45.7%–50.0% | 937 | 87 | 13 | Established | tew-v04-route-hunter (11.3 pp gap; 31 cells) |
| 162 | hunter-v14-cpp-hybrid-route-spacing | 46.6% | 44.9%–49.2% | 1408 | 101 | 13 | Established | hunter-v13-hybrid-route-spacing (4.5 pp gap; 100 cells) |
| 163 | drake-v05-sweep | 45.8% | 43.6%–49.0% | 234 | 15 | 13 | Established | drake-v04-beacon (3.8 pp gap; 40 cells) |
| 164 | drake-v09-density-tuned | 45.5% | 44.6%–48.3% | 312 | 12 | 13 | Established | drake-v10-dual-ewma (9.4 pp gap; 143 cells) |
| 165 | hunter-v11-route-distance-exploration | 45.4% | 43.4%–47.5% | 945 | 84 | 13 | Established | tew-v04-route-hunter (0.0 pp gap; 33 cells) |
| 166 | fry-v13-stateful-size-aware-2 | 45.3% | 43.1%–47.8% | 993 | 92 | 13 | Established | fry-v11-size-aware-hunters (12.4 pp gap; 97 cells) |
| 167 | hunter-v09-confidence-team-state | 45.3% | 43.0%–46.9% | 951 | 83 | 13 | Established | hunter-v10-confidence-enemy-state (5.0 pp gap; 90 cells) |
| 168 | hunter-v08-pearl-wide-sonar | 44.9% | 43.7%–47.2% | 932 | 83 | 13 | Established | hunter-v06-pearl-routing (1.2 pp gap; 82 cells) |
| 169 | hunter-v21-emergency-portals | 44.9% | 42.4%–48.2% | 984 | 83 | 13 | Established | hunter-v20-portal-scouts (5.0 pp gap; 189 cells) |
| 170 | tew-v04-route-hunter | 44.6% | 43.0%–48.1% | 134 | 22 | 13 | Established | hunter-v11-route-distance-exploration (0.0 pp gap; 33 cells) |
| 171 | hunter-v10-confidence-enemy-state | 44.2% | 41.8%–45.9% | 939 | 84 | 13 | Established | hunter-v09-confidence-team-state (5.0 pp gap; 90 cells) |
| 172 | formatted-hunter-v22 | 44.2% | 41.3%–49.0% | 92 | 6 | 13 | Established | hunter-v22-frontier-exploration (0.0 pp gap; 32 cells) |
| 173 | hunter-v06-pearl-routing | 44.2% | 41.3%–47.3% | 920 | 83 | 13 | Established | hunter-v08-pearl-wide-sonar (1.2 pp gap; 82 cells) |
| 174 | drake-v03-compact-production | 43.8% | 41.2%–46.7% | 334 | 23 | 13 | Established | drake-v07-soft-missions (5.4 pp gap; 121 cells) |
| 175 | drake-v10-dual-ewma | 43.6% | 41.9%–44.8% | 286 | 11 | 13 | Established | drake-v05-sweep (6.5 pp gap; 31 cells) |
| 176 | hunter-v02-team-growth | 43.5% | 40.2%–44.9% | 951 | 83 | 13 | Established | fry-v14-stateful-size-aware-3 (10.6 pp gap; 106 cells) |
| 177 | tew-v05-early-expansion | 42.3% | 39.6%–46.8% | 104 | 11 | 13 | Established | tew-v06-safe-fallback (0.0 pp gap; 31 cells) |
| 178 | hunter-v01-team-growth | 41.9% | 40.0%–43.6% | 944 | 83 | 13 | Established | fry-v14-stateful-size-aware-3 (9.9 pp gap; 101 cells) |
| 179 | hunter-v05-safe-attack-routes | 41.1% | 38.0%–43.0% | 985 | 86 | 13 | Established | hunter-v07-wide-team-state (2.3 pp gap; 87 cells) |
| 180 | tew-v06-safe-fallback | 41.0% | 34.2%–43.0% | 102 | 9 | 13 | Established | tew-v05-early-expansion (0.0 pp gap; 31 cells) |
| 181 | fry-v11-size-aware-hunters | 41.0% | 39.6%–44.7% | 987 | 87 | 13 | Established | fry-v12-stateful-size-aware-hunters (7.0 pp gap; 100 cells) |
| 182 | kraken-x01-notrade | 40.9% | 37.8%–41.3% | 999 | 95 | 13 | Established | tew-v03-cautious-forager (8.6 pp gap; 35 cells) |
| 183 | drake-v08-density | 40.5% | 38.2%–43.1% | 286 | 11 | 13 | Established | drake-v05-sweep (9.7 pp gap; 31 cells) |
| 184 | kraken-x04-nodoom | 40.2% | 36.8%–40.5% | 968 | 89 | 13 | Established | kraken-v05-safety (12.4 pp gap; 93 cells) |
| 185 | fry-v12-stateful-size-aware-hunters | 39.8% | 37.2%–42.4% | 966 | 88 | 13 | Established | fry-v11-size-aware-hunters (7.0 pp gap; 100 cells) |
| 186 | hunter-v07-wide-team-state | 39.4% | 37.7%–42.1% | 957 | 83 | 13 | Established | hunter-v05-safe-attack-routes (2.3 pp gap; 87 cells) |
| 187 | kraken-x03-noexit | 39.1% | 35.9%–40.7% | 991 | 92 | 13 | Established | kraken-s01-mid40 (15.2 pp gap; 92 cells) |
| 188 | hunter-v04-team-state-sonar | 38.9% | 37.6%–41.5% | 939 | 84 | 13 | Established | hunter-v07-wide-team-state (11.3 pp gap; 93 cells) |
| 189 | fry-v14-stateful-size-aware-3 | 38.5% | 36.0%–41.3% | 1407 | 105 | 13 | Established | hunter-v01-team-growth (9.9 pp gap; 101 cells) |
| 190 | kraken-v05-safety | 37.9% | 35.2%–38.8% | 946 | 86 | 13 | Established | kraken-x02-noini (12.0 pp gap; 92 cells) |
| 191 | kraken-s01-mid40 | 37.1% | 34.6%–38.7% | 968 | 88 | 13 | Established | kraken-v02-bigmap (2.9 pp gap; 85 cells) |
| 192 | hunter-v03-team-growth | 36.3% | 33.6%–39.1% | 942 | 83 | 13 | Established | hydra-v10-farmclean (13.6 pp gap; 92 cells) |
| 193 | kraken-v04-eval | 35.2% | 32.7%–36.1% | 2654 | 143 | 13 | Established | kraken-v02-bigmap (0.0 pp gap; 167 cells) |
| 194 | kraken-v02-bigmap | 35.0% | 32.6%–36.2% | 938 | 85 | 13 | Established | kraken-v03-judge-safe (0.0 pp gap; 89 cells) |
| 195 | kraken-s02-trade1 | 34.0% | 32.3%–36.9% | 947 | 83 | 13 | Established | kraken-v02-bigmap (5.9 pp gap; 93 cells) |
| 196 | kraken-x02-noini | 33.9% | 32.0%–35.3% | 912 | 83 | 13 | Established | kraken-v02-bigmap (9.4 pp gap; 85 cells) |
| 197 | hydra-v09-lanchester | 32.8% | 30.5%–35.7% | 1124 | 89 | 13 | Established | hydra-v08-claims (8.7 pp gap; 98 cells) |
| 198 | kraken-v03-judge-safe | 32.5% | 30.2%–34.1% | 940 | 83 | 13 | Established | kraken-v02-bigmap (0.0 pp gap; 89 cells) |
| 199 | drake-v02-hunt-feed | 32.2% | 29.4%–32.9% | 292 | 14 | 13 | Established | tew-v02-survive-forage (9.0 pp gap; 39 cells) |
| 200 | tew-v03-cautious-forager | 31.7% | 28.6%–35.9% | 100 | 8 | 13 | Established | tew-v02-survive-forage (3.0 pp gap; 33 cells) |
| 201 | drake-v01-survive-forage | 31.3% | 26.0%–34.9% | 182 | 8 | 13 | Established | tew-v02-survive-forage (0.0 pp gap; 42 cells) |
| 202 | hydra-v10-farmclean | 30.6% | 29.3%–33.9% | 963 | 86 | 13 | Established | hydra-v08-claims (2.4 pp gap; 84 cells) |
| 203 | tew-v02-survive-forage | 30.5% | 24.7%–33.3% | 108 | 9 | 13 | Established | drake-v01-survive-forage (0.0 pp gap; 42 cells) |
| 204 | kraken-x05-pstrong | 30.4% | 29.0%–31.8% | 958 | 85 | 13 | Established | kraken-s02-trade1 (7.7 pp gap; 97 cells) |
| 205 | hydra-v08-claims | 30.2% | 29.0%–32.3% | 928 | 84 | 13 | Established | hydra-v10-farmclean (2.4 pp gap; 84 cells) |
| 206 | leviathan-x02-riptide-viability | 29.1% | 26.8%–31.5% | 983 | 88 | 13 | Established | leviathan-x01-riptide-horizon (11.0 pp gap; 130 cells) |
| 207 | fry-v05-kamikaze-swarm | 28.4% | 24.1%–31.4% | 981 | 83 | 13 | Established | hunter-v02-team-growth (20.8 pp gap; 96 cells) |
| 208 | hydra-v07-farm-first | 28.4% | 25.7%–30.6% | 2424 | 134 | 13 | Established | hydra-v08-claims (8.0 pp gap; 162 cells) |
| 209 | hydra-v06-echo | 25.7% | 23.7%–29.2% | 920 | 84 | 13 | Established | hydra-v07-farm-first (9.5 pp gap; 163 cells) |
| 210 | fry-v07-two-children | 24.8% | 21.9%–27.0% | 965 | 83 | 13 | Established | fry-v09-pearl-seeker (0.0 pp gap; 96 cells) |
| 211 | kraken-v01-roles | 24.1% | 20.8%–26.2% | 971 | 85 | 13 | Established | leviathan-x01-riptide-horizon (13.4 pp gap; 99 cells) |
| 212 | fry-v09-pearl-seeker | 23.5% | 21.4%–25.7% | 962 | 83 | 13 | Established | fry-v07-two-children (0.0 pp gap; 96 cells) |
| 213 | leviathan-x04-charybdis-replies | 23.5% | 21.4%–24.6% | 1013 | 84 | 13 | Established | tew-v02-survive-forage (13.5 pp gap; 39 cells) |
| 214 | hydra-v01-core | 23.5% | 19.3%–29.8% | 92 | 6 | 13 | Established | hydra-v11-macro (4.7 pp gap; 32 cells) |
| 215 | leviathan-x01-riptide-horizon | 23.2% | 21.7%–26.4% | 1001 | 84 | 13 | Established | leviathan-x02-riptide-viability (11.0 pp gap; 130 cells) |
| 216 | fry-v03-portal-hunters | 22.4% | 18.3%–27.3% | 945 | 83 | 13 | Established | alik_test_bot (13.7 pp gap; 31 cells) |
| 217 | leviathan-v04-material | 22.0% | 20.5%–23.5% | 946 | 83 | 13 | Established | leviathan-v07-local-cache (3.2 pp gap; 77 cells) |
| 218 | hydra-v03-grower | 21.8% | 19.7%–24.0% | 966 | 83 | 13 | Established | hydra-v02-hunters (7.6 pp gap; 89 cells) |
| 219 | leviathan-v07-local-cache | 21.4% | 20.1%–22.0% | 965 | 84 | 13 | Established | leviathan-v06-confirmed-growth (0.0 pp gap; 96 cells) |
| 220 | fry-v06-one-child | 21.0% | 20.2%–22.7% | 946 | 85 | 13 | Established | fry-v08-pre-swarm-defense (0.0 pp gap; 82 cells) |
| 221 | fry-v08-pre-swarm-defense | 20.6% | 19.2%–22.7% | 956 | 85 | 13 | Established | fry-v06-one-child (0.0 pp gap; 82 cells) |
| 222 | alik_test_bot | 20.1% | 18.5%–21.4% | 92 | 6 | 13 | Established | hydra-v11-macro (9.1 pp gap; 33 cells) |
| 223 | fry-v10-pearl-seeker-center | 20.1% | 17.7%–21.3% | 947 | 84 | 13 | Established | hydra-v01-core (11.3 pp gap; 31 cells) |
| 224 | fry-v02-dragon-hunters | 20.1% | 17.5%–22.2% | 928 | 83 | 13 | Established | alik_bot_v2 (13.3 pp gap; 30 cells) |
| 225 | leviathan-v06-confirmed-growth | 19.7% | 17.8%–21.9% | 956 | 83 | 13 | Established | leviathan-v07-local-cache (0.0 pp gap; 96 cells) |
| 226 | leviathan-v05-tail-risk | 19.6% | 17.5%–20.9% | 966 | 83 | 13 | Established | leviathan-v07-local-cache (7.8 pp gap; 83 cells) |
| 227 | hydra-v02-hunters | 19.0% | 17.2%–21.1% | 986 | 83 | 13 | Established | hydra-v01-core (6.8 pp gap; 37 cells) |
| 228 | hydra-v11-macro | 18.5% | 16.2%–20.3% | 976 | 83 | 13 | Established | hydra-v01-core (4.7 pp gap; 32 cells) |
| 229 | fry-v04-escorts | 13.0% | 11.3%–14.3% | 1000 | 84 | 13 | Established | tew-v01-local-forager (4.2 pp gap; 36 cells) |
| 230 | fry-v01-danger-levels | 12.5% | 11.9%–15.0% | 946 | 83 | 13 | Established | fry-v08-pre-swarm-defense (11.8 pp gap; 72 cells) |
| 231 | tew-v01-local-forager | 4.0% | 2.8%–6.5% | 110 | 10 | 13 | Established | leviathan-v02-expansion (2.6 pp gap; 38 cells) |
| 232 | leviathan-v01-evaluator | 2.4% | 1.7%–3.2% | 982 | 84 | 13 | Established | leviathan-v03-population (1.1 pp gap; 92 cells) |
| 233 | alik_bot_v2 | 1.6% | 1.1%–3.7% | 104 | 7 | 13 | Established | leviathan-v02-expansion (1.2 pp gap; 41 cells) |
| 234 | leviathan-v03-population | 1.5% | 1.0%–1.9% | 949 | 84 | 13 | Established | leviathan-v02-expansion (0.0 pp gap; 107 cells) |
| 235 | leviathan-v02-expansion | 1.4% | 0.9%–1.7% | 1008 | 84 | 13 | Established | leviathan-v03-population (0.0 pp gap; 107 cells) |
| 236 | formatted-hunter-v22-python | 0.1% | 0.0%–0.1% | 64 | 13 | 13 | Established | Insufficient overlap |

Matching record sources: {"benchmark": 12860, "bot_field_tournament": 35577, "compare_bot": 8799, "leviathan_lab": 684}.

Reference panel: ouroboros-v10-beacon, hunter-v20-portal-scouts, hydra-v07-farm-first, kraken-v04-eval, avery-v05-strict-crown, tew-v12-mid-support.

Refresh health is recorded in `status.json`; `latest.json` includes map profiles, head-to-head scores and source/map fingerprints. The earlier inline chart remains a snapshot.
