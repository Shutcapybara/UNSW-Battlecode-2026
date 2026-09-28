# Javert x01: execution-contract base

Exact behaviour fork of `aramis-v02-frontier` with `FRONTIER_MODE = 0` (the
`aramis-x08-density-control` configuration): Monte Christo v07 density state
(D1) and radio (R1), no macro candidates, contract I1 / candidates C2 /
executor E2 / features F1 / policy P2.

The Javert lineage code carries four further switches (LEN_DENSITY, POLICY3,
PORTAL_SCOUT, SPACE_TRADE), all off in this cell. Every javert-x0* cell shares
identical executable files and differs only in `settings.py`; with all
switches off the behaviour is Aramis v02 mode 0, so switch isolation is the
comparison unit. See the Javert report (`../../docs/javert.md`) for the study.
