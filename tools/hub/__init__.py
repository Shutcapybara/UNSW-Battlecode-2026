"""JKS hub: the shared research and live-validation record for Just Keep Swimming (team 7).

Day-one scope (director decision D-001, 2026-09-28): an observer/decision cycle that reads the
legacy live-validation system's durable files, keeps the hub database, scores the queue, writes
tick summaries and two-hour review packets, mirrors them into the repository, and keeps the legacy
worker alive. Mutating API calls stay with the legacy executor until the hub actuator is cut over.
Standard library only; Python 3.10+.
"""
HUB_SCHEMA_VERSION = 1
