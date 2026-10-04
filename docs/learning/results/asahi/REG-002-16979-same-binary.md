# REG-002: submission 16979 is the gated bot (D-064 §B condition 5)

Asahi, 4 Oct 2026 23:12Z. Method 1 of D-064 §B.5: the runtime fingerprint recomputed on the archive.

- Archive: `build/daichi/ls1/16979-asahi-05-kz12-k16.zip` (main checkout), 3,924,654 B,
  sha256 `585183301571e34d104e2deefa49374d2f5704a403ee23d999370760c7c773a3` (equal to Daichi's 22:52Z line).
- Fingerprint: `tools/analysis/features/run_panel.runtime_fingerprint`'s algorithm (sorted relative names of files
  with a source suffix or named `bot.toml`; sha256 over name NUL bytes NUL), applied to the archive members read in
  memory: **43bd2d4fc7a8baac6d8f14d22a6a0a8eb9c33cc2ca85ee12cce5b770a3eff1ad**, 13 files.
- Gated runs: `build/asahi/runs/asahi-05-kz12-k16/43bd2d4f/{pool,gen}/run.json` carry the same 64-hex fingerprint,
  runtime unswbc 1.2.3, seeds [1, 2, 3] (pool 816, gen 1,392 index rows). The bot directory on r/asahi recomputes to
  the same value.
- Per file: all 13 fingerprinted members are byte-identical to `bots/asahi-05-kz12-k16/` (the symlinked
  `hb1_direction_compact.hpp` resolves to sha256 1c3f8974…, 12,944,565 B, in both). The archive's other three members
  (`CANDIDATE.toml`, `README.md`, `.gitignore`) are outside the fingerprint and are not compiled.
- Scope: this proves the uploaded source equals the gated source. The server compiles it itself; LS-1's games played
  without fault are the evidence that it builds there.

**Condition 5: met.** No Weakhold re-run was queued (not needed under the either/or of §B.5).
