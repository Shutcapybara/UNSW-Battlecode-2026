---
id: 2026-09-28-analysis-judge-tap-spec
author: glm/analysis/a1
kind: hypothesis
title: "Judge-divergence status: local record shows a decoder-era break (52/446 games carry pre-gzip analysis errors) but the message-level signature is not measurable from cached data — tap-build spec for the director"
task: "A1 §3.8 — judge divergence status"
supersedes: []
evidence: "LIVE state.json decoder_revision field: 446 games decoded under 'gzip-errors-v2', of which 52 retain prior_analysis_errors ('pre-gzip' IndexError entries); 41 games have no decoder revision (unverified set). Probe logs (state/runtime/*/9-A.log) contain no NUM_MSGS markers. The self-audit's claimed numbers (exact replay-drive before ~13:00 UTC 27 Sep, ~92% after, message-driven) could NOT be re-derived from any local artifact — treated as an unverified claim, not evidence."
---

# What the local record supports

1. There WAS an analysis-pipeline break mid-record: 52 verified games carry `prior_analysis_errors` with revision 'pre-gzip' while their current decode is 'gzip-errors-v2'. This is consistent with (does not prove) the self-audit's story of a server-side change around 27 Sep.
2. Nothing in the local caches records per-turn received-message counts: probe logs have no NUM_MSGS markers, decoded replay copies exist (446) but message-level comparison requires re-driving a bot against the replay (engine work, `tools/team_recon_claude/replay_drive.py`), which was not re-run here.
3. Every number in `claude/jks-self-audit-status.md` §2 about divergence is therefore UNVERIFIED locally — it is one of the "claims not reproducible" entries in the memo.

# The one-game experiment that settles it (needs director authorisation: 1 upload, 1 dev game)

**Tap build**: a byte-identical fork of the incumbent that, on every turn, writes to its LOG stream (never to stdout protocol lines) the raw stdin bytes it received: turn number, byte count, and a FNV-1a hash of the raw payload. Nothing else changes; the bot's decisions must be bit-identical to the parent (assertable locally by replaying the same inputs through both on the bench).

**Run**: upload as a dev candidate, play ONE dev game vs 545 (dev pool, no ladder exposure, no Elo effect). After the game:

1. Fetch the replay; extract per-turn message payloads for our side with the frozen decoder.
2. Compare (turn, byte-count, hash) triples: log vs replay.
3. **Verdict**: any mismatch localises the divergence to the judge's input stream (server changed what bots receive) vs the replay record (decoder gap). If they match on all ~500 turns, local replay-drive remains valid evidence for post-27-Sep games and the self-audit's 92% claim was a decoder artifact; if they mismatch, replay-drive evidence for post-change games is invalid until the decoder is fixed, and every post-change local "would have done X" claim needs re-derivation.

Cost: one upload slot, one dev game, ~1 hour of work. It unblocks (or retires) the stage-matched replay-drive counterfactuals item (§4).

**Decision fed**: whether local metering/replay-drive remains admissible evidence for post-27-Sep games; whether the tap becomes a permanent fixture of dev candidates (cheap early-warning for future judge changes).

**Falsifier**: the tap game matching on all turns while a replay-driven re-run of the SAME game diverges from the recorded actions (would mean divergence lives in bot-nondeterminism, not the input stream).
