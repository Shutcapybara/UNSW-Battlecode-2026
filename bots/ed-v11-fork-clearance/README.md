# Ed v11: strict split-child clearance

- **Parent:** `ed-v02-split-intent` (which branches from frozen `ed-v00-serre-control`).
- **One change:** while a new child holds a fresh parent FORK packet, targets within the existing radius and eight-turn child age window receive zero value instead of the v02 soft value factor `0.35`.
- **Purpose:** test whether a strong temporary clearance signal stops newborns from returning to the parent’s resource pocket, especially around narrow passages, while preserving the parent’s short-lived intent handoff.
- **Off switch:** `fork_intent = 0` reproduces v00 behavior; with intent on, this variant differs from v02 only in `fork_value_scale`.
- **Risk:** if no independent safe target is reachable, a child may waste turns or the parent target’s area may be the only viable route. No path is hard-blocked; only resource-target value is removed.
