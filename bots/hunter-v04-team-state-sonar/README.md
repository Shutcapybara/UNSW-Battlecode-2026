# hunter-v04-team-state-sonar

This version extends hunter-v02 with safe portal exploration. Only the
largest known friendly dragon enters growth mode. It focuses on growth from
round 450 onward, or from round 400 when the largest known enemy is longer than
the largest known friendly dragon. It keeps a two-segment safety buffer before
treating the team as comfortably ahead. The largest dragon gets priority over
safe pearls even when a teammate is closer; other dragons may still collect
pearls when the largest dragon is elsewhere. Other dragons remain in
hunter/exploration mode when they are not the growth owner. A known-smaller
dragon may also take a completed exploratory portal trip, including one with
no immediate pearl reward, when at least four friendly dragons are alive.
It may enter a visible portal with only one currently known endpoint; the next
observation records the destination endpoint and enables normal round-trip
planning.
This version extends hunter-v03-team-growth with the v1.0 64-bit directional
sonar protocol. Each dragon broadcasts its current ID, length, wrapped head
position, and round on all four cardinal channels. Teammate state is refreshed
from those snapshots and expires after 20 rounds. A close-range face-off sends
the higher-priority MOVE_ASIDE signal on the forward channel while the other
three channels continue sharing state. The bot also consumes the new sonar
echo record so the input stream remains aligned with the updated helper.

A fry-v03-portal-hunters variant that only deliberately attacks a visible enemy dragon
when the enemy has more visible body segments than the attacking dragon's
current length. It uses as many movement steps as its current length allows,
so a smaller dragon can commit to a multi-move attack against a larger target.

Enemy size is estimated conservatively from body segments visible in the local
observation window. Hidden enemy segments are not counted, so the bot may pass
up some valid attacks rather than making an unsafe size assumption.

The portal, pearl-growth, exploration, and emergency-survival behavior is
otherwise inherited from fry-v03-portal-hunters.
