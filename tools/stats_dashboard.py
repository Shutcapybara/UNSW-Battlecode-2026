#!/usr/bin/env python3
"""Inspect the rebuilt local statistics ledger."""
import argparse
from pathlib import Path
from stats_store import StatsStore, DEFAULT_DIR

def main():
    p = argparse.ArgumentParser(); p.add_argument('--root', type=Path, default=DEFAULT_DIR)
    s = StatsStore(p.parse_args().root)
    try:
        print(f"{'Bot':32} {'Played':>7} {'W':>4} {'D':>4} {'L':>4} {'Err':>4} {'Pts':>5}")
        for r in s.standings(): print(f"{r['bot'][:32]:32} {r['played']:7} {r['wins']:4} {r['draws']:4} {r['losses']:4} {r['errors']:4} {r['points']:5}")
    finally: s.close()
if __name__ == '__main__': main()
