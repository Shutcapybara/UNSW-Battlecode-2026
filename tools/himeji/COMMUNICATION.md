# Himeji analyst communication lane

Established 4 October 2026 at the user's request. Himeji now owns live-data connectivity/collection oversight,
versioned analytical refreshes, current top-team anatomy and investigation of possible concealed active-bot regimes.
The previous Antioch-only restriction is superseded for Himeji by this explicit assignment.

The durable inbox/outbox is `docs/hub/BOARD.md` on the lane branches. Every message has a unique Himeji ID,
addressee, one numerical result or concrete question, evidence pointer, and requested decision/next action.
Replies reference the originating ID. Unanswered IDs live at the top of `claude/himeji-status.md`.
Read `origin/main` and peer branch boards before each half-hour unit; a merge into main is not required to see a message.
Keep append-only history and both sides of disagreements. The keeper remains responsible for main merges.

Routes:

| Recipient | Durable branch / status | Direct chat route |
|---|---|---|
| Antioch, analyst | origin/r/antioch; claude/antioch-status.md | Not visible in current app inventory; use board |
| Nara, analyst | origin/r/nara; claude/nara-status.md | Not visible in current app inventory; use board |
| Rome, tester | origin/r/rome; claude/rome-status.md | Existing chat “Run P2-T hypothesis tests”, 01a0f76f-dbbc-7f80-b4ec-802e5549522f; board is default |
| Carthage, tester | origin/r/carthage; claude/carthage-status.md | Board |
| Kyoto, tester | origin/r/kyoto; claude/kyoto-status.md | Board |
| Director | origin/main; docs/hub/BOARD.md | Board |

Within the user's authorized analyst coordination workflow, an actionable targeted message may also be sent to
an identified existing analyst chat when available. Include its board ID/pointer, and record the response back
on the board. Do not create a new chat, broadcast to historical tasks, or restart another lane just to establish
connectivity. Current inventory exposes Rome resuming work but no separate Antioch/Nara chat; do not pretend a
direct message reached them. No direct messages were sent during setup.

Himeji's recurring cycle is the delivery mechanism: every30minutes inspect replies/results, acknowledge new
addressed questions, and give each new tester result a numerical evidence-backed reading. Allow bounded parallel
work on the shared Mac and coordinate through board/status rather than duplicating downloads or queries.
