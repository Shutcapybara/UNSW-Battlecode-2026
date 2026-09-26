"""Version switches are experiment artifacts; no runtime tuning."""
VERSIONS = dict(contract='I1', candidates='C2', executor='E2', features='F1',
                policy='P2', state='D1', communication='R1', roles='MC01')
FEATURE_VERSION = 1
EXECUTOR_VERSION = 0
TRACE = False

# 0 = information/radio control; 1 = advance and withdraw; 2 = withdraw only
FRONTIER_MODE = 0

# Javert lineage switches. Off = exact Aramis v02 (mode 0) behaviour; each
# controlled cell enables a strict superset so single-switch comparisons hold.
LEN_DENSITY = 1   # D2/R2: type-7 length packets, length field built but unconsumed
POLICY3 = 1       # F2/P3: phase/population/openness facts consumed by policy scores
PORTAL_SCOUT = 0  # C3: nominate a SCOUT toward the nearest unpaired portal edge
SPACE_TRADE = 0   # C4/E3: population-saturated early trade permission via candidate margin
