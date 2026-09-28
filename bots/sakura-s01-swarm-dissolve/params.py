"""sakura-s01-swarm-dissolve: macro schedule (all map-conditioned knobs).

The five-layer framework of docs/design-framework.md, generation S1:
swarm through the opening, material/survival through the middle, one
protected crown fed by adjacent, recipient-first dissolution from a
map-conditioned onset.  Every number below is a hypothesis parameter;
the 2x2 ablation flips prod_enabled / dissolve_enabled on the same
seeded fixtures.
"""
PARAMS = {
    # --- arm switches (2x2 ablation; control = ouroboros-v10-beacon) ------
    "prod_enabled": 1,        # SPLIT-2 swarm to unit_target (else v10 targets)
    "dissolve_enabled": 1,    # escort + adjacent dissolve (else no feeding at all)
    "cert_enabled": 1,        # birth certificate over the backward ray
    "strike_enabled": 0,      # voluntary parity-priced strikes (salvage trades stay)
    "hyst_enabled": 1,        # target cache with switching margin
    # --- production (H-prod) ----------------------------------------------
    "unit_target": 64,        # production stops at the cap ...
    "unit_target_cells": 24,  # ... but never denser than one dragon per 18 cells
    "produce_until": 100,     # ... lambda_unit holds to here, ...
    "produce_stop": 380,      # ... then decays linearly to zero by here
    "split_child_len": 2,     # production child length
    "split_min_len": 4,       # never produce below this parent length
    # --- crown + dissolution (H-dissolve) ----------------------------------
    "crown_elect_from": 250,  # crown election starts (beacons, id-staggered)
    "crown_stagger": 40,      # election delay window: (id*7919)%crown_stagger
    "onset_portals": 300,     # dissolve onset on Portals / Slithery Fight
    "onset_default": 400,     # ... everywhere else
    "feed_max_len": 3,        # dissolve only if L <= this
    "feed_radius": 30,        # escort only within this route distance of crown
    "recipient_eats_first": 1,  # dissolve only if crown can eat the corpse now
    # --- momentum (H-cert companions) ---------------------------------------
    "hyst_margin": 2.0,       # length units before switching targets
    "split_crowd_early": 16,   # swarm-push split gates (pre produce_until)
    "split_danger_early": 0.45,
    "target_ttl": 12,         # rounds a cached target stays sticky
    "cert_target_ttl": 15,    # rounds an inherited target guides a newborn
}
