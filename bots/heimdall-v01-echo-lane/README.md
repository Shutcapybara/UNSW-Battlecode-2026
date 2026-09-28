# Heimdall v01 — echo lane

Heimdall starts from Fenrir v18, whose bounded child-site handoff and
arrival-ready resource timing scored 77–43 over its broad reference panel.
That chassis descends from Bifröst v01 and retains its portal-exit memory.

This first Heimdall change gives protocol sonar echoes a directional consumer.
Every fourth action, when crown, prey, and split-handoff traffic is not queued,
the bot replaces lower-priority sonar packets with one isolated scan ray. It
remembers that ray's origin and direction. If its next-turn echo reports an
enemy body or head, move scoring applies a short-lived, low-weight penalty to
cells on that lane. Other turns retain the inherited radio schedule.

The isolated scan is needed because the engine returns aggregate counts across
all rays without identifying which direction produced each hit. This changes
no map knowledge or protocol framing. The policy uses enemy-head echoes more
strongly than body echoes and expires both quickly because the report is stale
after the opponent moves.

See `docs/heimdall-family.md` for paired benchmark results and iteration
choices.
