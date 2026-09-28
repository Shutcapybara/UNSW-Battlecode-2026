# Heimdall v09 — short echo-conditioned bed timing

V09 starts from the measured v05 echo-conditioned policy and halves its bed
wait horizon. With no enemy contacts in the previous echoes it values beds up
to six rounds ahead; enemy-body contacts shorten that window by three rounds,
and enemy-head contacts by six. Fenrir's portal-risk policy, child-site
separation, and radio schedule remain unchanged.

The rule uses aggregate echoes only as a local activity signal; it does not
claim to know which direction or coordinate produced a hit.
