# ouroboros-b01-bifrost-feed360

bifrost-v01-portal-memory (recovered, hash-verified submission 8540) with its own `override.py` extended by
feed_base=100, grow_from=split_stop=340 (base: 40 / 380 / 380). On a 32x32 map feeding starts at
~r362 instead of ~r422. Hypothesis from the team-7 audit: bifrost converts ~100 rounds later than
Vibing++ and loses round-limit games on longest length. Single-factor test; no other code changes.
