# hunter-v14-cpp-hybrid-route-spacing

Experimental C++ port of `hunter-v13-hybrid-route-spacing`. It retains V13's
reachable attacks, expiring teammate-size evidence, pearl route ownership, and
hybrid live/static teammate spacing.

Validation: six action/SONAR parity tests and inherited size-aware tests pass.
It scored 22W/22L (66 points) in the paired 11-map pool; Python V13 scored
23W/21L (69 points). There were no runner errors or invalid actions, but C++
V14 lost all four `big_empty` games while V13 won three of four. The 500-round
`big_empty` sandbox mirror completed with 64 dragons alive per side and no CPU
or action failures; peak cost was 10.4M CPU points. The port has substantial
runtime headroom but is not a tactical improvement yet. Diagnose the
`big_empty` losses before considering submission.
