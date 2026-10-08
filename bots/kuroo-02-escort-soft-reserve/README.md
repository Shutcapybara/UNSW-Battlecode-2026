# kuroo-02-escort-soft-reserve

New Kuroo family snapshot based on `akaashi-12-queen-strike-escort`. Preserves its strategy and permits
a worker with no nonfatal immediate move to spend the final reserved unit slot
on a verified tail escape split. Match 1427506, A405, protocol round 199.

Local experimental candidate; no strength promotion or server deployment.
See `docs/kuroo-family.md` for evidence and limitations.

Routine production receives a gradual capacity penalty in the last eight
slots (scaled down for small unit limits), including the loss of free sprint
steps when a parent is shortened. Emergency splits are exempt.
