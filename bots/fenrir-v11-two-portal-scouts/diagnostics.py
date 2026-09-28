"""Opt-in native logging of selected, surviving moves for hazard fitting.

LOG and action share protocol.py's one output flush. Never enabled in releases.
Labels are extracted later from replay death events, not visible to the bot.
"""
import json
import sys
import world as w
import tactics as tx


def trace_threats(work):
    kind, arg = work["selected"]
    if kind != "move":
        return
    st, nb, _, _ = tx.sim(arg, w.body)
    if st != "ok" or tx.BLIND[0]:
        return
    ts = work["threat"].get(nb[-1], ())
    if not ts:
        return
    rows = [[eid, [steps, len(nb), el, int(eid in w.cut), int(eid > w.ME),
                    w.RND, w.UNITS, len(ts), w.NC]] for steps, eid, el in ts]
    sys.stdout.write("LOG MC_RISK " + json.dumps(rows, separators=(",", ":")) + "\n")
