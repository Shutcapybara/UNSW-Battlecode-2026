# Heimdall v02 — echo risk prior

V02 keeps Fenrir v18's bounded child-site handoff and portal-aware search,
but restores Bifröst v01's bed timing and unseen-exit risk. This separates
Fenrir's useful split behavior from its more aggressive resource/portal
valuation changes.

It consumes `world.echo` directly without changing sonar traffic. The engine
returns aggregate hit counts with no direction, so enemy-body and enemy-head
hits only provide a weak global activity prior. The policy uses that prior to
raise unseen portal-exit risk and slightly scale existing local head-threat
costs. It does not infer a location from an aggregate count.

V01 tested isolated directional scans, but overrode all lower-priority radio
messages and failed to protect Fenrir's newer split-packet tag. That version's
partial screen is preserved in `experiment_data/`; v02 avoids both issues.
See `docs/heimdall-family.md` for results.
