# Tyr V02 — rejected portal-egress implementation

This frozen experiment is retained for its benchmark record. A patch-script error left `recent_portal_penalty` undefined; the bot fell back to its emergency move policy. It recorded no pearl collection and no portal traversals on Queen of Spades. The tournament runner counted valid fallback actions, so it reported no runner errors.

Do not use this as a strategy comparison. Tyr V03 contains the corrected paired-portal experiment. See [`docs/tyr-family.md`](../../docs/tyr-family.md).
