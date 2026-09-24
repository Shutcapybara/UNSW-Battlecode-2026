"""Selected exploratory profile. Master-off reproduces Leviathan v09."""
PARAMS = {'pearl.prepos': 1, 'pearl.confirmed_only': 1, 'estuary.enabled': 1,
          # The bounded geometry option remains available for exploration,
          # but its first paired screen regressed all three Stronghold cases
          # that the same doctrine wins without it. Do not ship that veto.
          'estuary.safety': 0}
