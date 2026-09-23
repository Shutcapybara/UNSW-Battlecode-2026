# hunter-v02-team-growth

This version extends hunter-v01 with an adaptive growth transition. Only the
largest known friendly dragon enters growth mode. It focuses on growth from
round 450 onward, or from round 400 when the largest known enemy is longer than
the largest known friendly dragon. It keeps a two-segment safety buffer before
treating the team as comfortably ahead. The largest dragon gets priority over
safe pearls even when a teammate is closer; other dragons may still collect
pearls when the largest dragon is elsewhere. Other dragons remain in
hunter/exploration mode when they are not the growth owner.
Teammate lengths are shared through the status sonar message and expire after
20 rounds; MOVE_ASIDE remains higher priority than status broadcasts.

A fry-v03-portal-hunters variant that only deliberately attacks a visible enemy dragon
when the enemy has more visible body segments than the attacking dragon's
current length. It uses as many movement steps as its current length allows,
so a smaller dragon can commit to a multi-move attack against a larger target.

Enemy size is estimated conservatively from body segments visible in the local
observation window. Hidden enemy segments are not counted, so the bot may pass
up some valid attacks rather than making an unsafe size assumption.

The portal, pearl-growth, exploration, and emergency-survival behavior is
otherwise inherited from fry-v03-portal-hunters.
