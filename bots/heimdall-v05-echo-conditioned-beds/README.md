# Heimdall v05 — echo-conditioned bed timing

V05 combines v04's Bifröst improvement with a sonar-conditioned bed horizon.
With no enemy contacts in the previous echoes it values beds up to twelve
turns before arrival; enemy-body contacts shorten that window by six turns,
and enemy-head contacts shorten it by twelve. Fenrir's portal-risk policy,
child-site separation, and radio schedule remain unchanged.

The rule uses aggregate echoes only as a local activity signal; it does not
claim to know which direction or coordinate produced a hit.
