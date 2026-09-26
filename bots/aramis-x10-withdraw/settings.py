"""Version switches are experiment artifacts; no runtime tuning."""
VERSIONS = dict(contract='I1', candidates='C2', executor='E2', features='F1',
                policy='P2', state='D1', communication='R1', roles='MC01')
FEATURE_VERSION = 1
EXECUTOR_VERSION = 0
TRACE = False

# 0 = information/radio control; 1 = advance and withdraw; 2 = withdraw only
FRONTIER_MODE = 2
