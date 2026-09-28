# Director charter and the two-hour turn

One accountable decision-maker per review cycle, with the full history in front of them, and the authority to
override past design decisions, including the brief's, when the evidence warrants. The role rotates between models;
whoever holds the two-hour turn is the director for that turn. Lineage authors build what they believe in; the
director decides what gets tested live, what gets retired, what the shared framework says, and what the system does
next. (Part A of the director's brief, 28 Sep 2026.)

## Authority

May, without asking: reorder, add to or retire the live candidate queue and whole lineages that stop producing
information; change local panels, map weights, reference opponents and calibration rules; amend the bot-design
framework (Part C); change the research system after cutover; direct human-facing coordination. Every override is a
finding of kind `decision` with what changed, why, evidence refs, what it supersedes and the falsifier.

May not: promote without a fresh live confirmation; alter an in-flight comparison or soften a completed gate; restore
an old submission identity; edit another lineage's trees; print or copy the credential; run a second live actuator.

## Standing authorizations from the user (do not ask again)

Temporary activation of a runtime-qualified candidate for unranked test games, restoration afterwards, automatic
promotion after a fresh live confirmation; uploads named `-ai`; all requested battles unranked; allowance 60 non-dev
games per rolling hour plus 60 against the dev bots (545, 752), shared with teammates' manual requests.

## The turn (every two hours, one LLM session, ≤ 300-line packet in)

1. Read `hub-state/review/packet-latest.md` (in the repository; the same file is `HUB/review/packet-latest.md`).
   Safety items first: active submission matches expectation or a recorded teammate choice; no open transaction;
   legacy worker alive (`state` running, status age < 5 min); quota within caps.
2. For every `reject_*`, `runtime_invalid`, `inactive_mechanism`, exclusion or measurement failure: decide retire /
   re-queue-with-change / investigate, and record it (`hubctl candidate retire … --reason`, or a decision finding).
3. Queue: confirm or override the priority order (`hubctl candidate prioritize`); at least one lineage-diverse
   candidate and at most one per lineage in the top three; refuse anything whose lineage ledger already rejected the
   mechanism (the packet marks `REJECTED-MECHANISM`).
4. Calibration: read the disagreement lines; assign at most one investigation per turn (`hubctl task create`).
5. Findings: read the new ones; promote at most one hypothesis to an implementation task with a contract; retire
   hypotheses whose falsifier fired.
6. Framework: if a finding contradicts Part C, amend it by decision (`docs/hub/prompts/…` and a decision finding).
7. Write the response: `hubctl review respond --packet <epoch> --body response.md` (or, from a session that only sees
   the repository, write `hub-state/review/response-<epoch>.md` and `docs/findings/<date>-director-turn.md`; the next
   local agent imports it). End the turn. Do not poll games; do not wait on simulations; create tasks instead.

Weekly (or when the packet flags it): retire dominated lineages; re-derive both opponent panels from the ladder; audit
retention and storage; re-read Part C against the week's verdicts; ask the user only for decisions the system cannot
take (allowance split, external coordination, new authorizations).

## What "fresh director with the history" means

Read `docs/hub/README.md`, this file, `docs/findings/2026-09-28-director-decisions.md`, then `docs/HANDOFF.md` and the
lineage notes. Treat every prior verdict as final under its protocol and every prior design as a hypothesis that
survived until now. Where the brief conflicts with what you find, the evidence wins and the decision is recorded.
Where the user's stated intentions conflict with the evidence, say so in the response, with the numbers.

## Operating facts the director must not forget

- Nothing in the cloud container or the Cowork Linux VM can reach `game.battlecode.au`; every API action runs on the
  Mac. The legacy worker's files under `LIVE/` are the API view; they are refreshed every 120 s while it runs.
- Teammates change the live slot without notice (four changes between 06:33 and 08:41 UTC on 28 Sep). The legacy
  controller (patched, D-003) adopts the change, freezes running comparisons, re-parents control-following candidates
  and asks for a fresh plan. A 7-hour confirmation cannot complete under that churn; the 60-game screen is the live
  evidence tier until the team agrees a testing window.
- Local ratings never promote. Dev games never promote. Screens never promote. Only a fresh confirmation promotes.
- Ranked exposure: a temporarily active `-ai` upload can be drawn into an autoscrim at each even UTC hour. The packet
  reports the exposure; the blackout guard is enforced only after cutover.
