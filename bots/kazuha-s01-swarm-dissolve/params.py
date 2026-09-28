"""kazuha-s01 macro schedule (S1 build prompt 4.2).  main.py loads PARAMS
from this file; the 2x2 arms override single keys here (prod_swarm,
dissolve_on, cert_enabled)."""
PARAMS = dict(
    # production: tail-heavy swarm while lam_unit > 0
    unit_target=64,
    produce_until=100,
    produce_stop=380,
    split_child_len=2,
    split_min_len=4,
    split_crowd_max_opening=14,
    # crown / conversion
    crown_elect_from=250,
    onset_early=300,        # Portals-like (small + portal-dense) and Slithery-like
    onset_default=400,
    feed_max_len=3,
    feed_radius=30,
    recipient_eats_first=1,
    crown_demote=3,
    beacon_ttl=3,
    # mechanisms
    strike_enabled=0,
    cert_enabled=1,
    hysteresis_margin=1.0,
    hyst_tgt_ttl=3,
    # 2x2 arm switches
    prod_swarm=1,
    dissolve_on=1,
)
