# hunter-v01-team-growth

This version extends stateful size-aware hunters v3 with team-length estimates.
Dragons broadcast their current length through the sonar channel, remember
recent teammate sizes, and let the largest known friendly dragon prioritize
late-game growth when no visible threat exists. Smaller dragons spread instead
of competing for growth pearls. MOVE_ASIDE remains higher priority than status
broadcasts.

A fry-v03-portal-hunters variant that only deliberately attacks a visible enemy dragon
when the enemy has more visible body segments than the attacking dragon's
current length. It uses as many movement steps as its current length allows,
so a smaller dragon can commit to a multi-move attack against a larger target.

Enemy size is estimated conservatively from body segments visible in the local
observation window. Hidden enemy segments are not counted, so the bot may pass
up some valid attacks rather than making an unsafe size assumption.

The portal, pearl-growth, exploration, and emergency-survival behavior is
otherwise inherited from fry-v03-portal-hunters.
