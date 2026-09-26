"""Opt-in native logging of selected actions for offline analysis.

LOG and the action share protocol.py's one output flush. Never enabled in
releases (params training_trace = 0).  Trace tags are ATHOS_RISK /
ATHOS_INTENT: reuse of monte_christo trace tooling requires retargeting the
prefix.  Labels are extracted later from replay events, not visible to the
bot.
"""
import json
import sys
import world as w
import tactics as tx
import roles


def trace_threats(work):
    kind, arg = work["selected"][1]
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
    sys.stdout.write("LOG ATHOS_RISK " + json.dumps(rows, separators=(",", ":")) + "\n")


def trace_intent(work):
    plan = work["plan"]
    row = [w.RND, work["intent"], work["intent_note"], plan["kind"], plan["target"],
           round(work["score"], 2), w.LEN, w.UNITS, roles.ROLE[0]]
    sys.stdout.write("LOG ATHOS_INTENT " + json.dumps(row, separators=(",", ":")) + "\n")
