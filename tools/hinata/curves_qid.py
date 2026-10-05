"""Queen id per team: the team's lowest initial dragon id (ids follow the map's DRAGON lines). Shared by curves*.py."""
import sys; sys.path.insert(0, '.')
from tools.analysis.features import frame
def queen_ids(maptext):
    q = {}
    for i, (t, b) in enumerate(frame.terrain(maptext)[0]['dragons']): q.setdefault(t, i)
    return q
