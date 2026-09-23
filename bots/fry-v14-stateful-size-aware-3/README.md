# Stateful size-aware hunters v3

This version adds pearl decision-making to the stateful size-aware hunter.
Recent pearl observations receive a freshness bonus. A dragon pursues a pearl
only when it is the closest visible teammate to that pearl; lower dragon IDs
break equal-distance ties. When no pearl is clearly owned, normal movement
continues to favor separation from teammates. It uses no pearl-claim protocol.

A fry-v03-portal-hunters variant that only deliberately attacks a visible enemy dragon
when the enemy has more visible body segments than the attacking dragon's
current length. It uses as many movement steps as its current length allows,
so a smaller dragon can commit to a multi-move attack against a larger target.

Enemy size is estimated conservatively from body segments visible in the local
observation window. Hidden enemy segments are not counted, so the bot may pass
up some valid attacks rather than making an unsafe size assumption.

The portal, pearl-growth, exploration, and emergency-survival behavior is
otherwise inherited from fry-v03-portal-hunters.
