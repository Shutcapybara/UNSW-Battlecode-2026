"""Bifröst v15: shorten bed-wait value only on compact maps."""
OVERRIDE = {
    "bed_wait_compact": 6.0,
    "bed_wait_compact_cells": 625,
    "bed_wait_compact_until": 200,
}
