"""Bifröst v16: discourage only persistent loops through empty, safe cells."""
OVERRIDE = {
    "empty_repeat_threshold": 2,
    "empty_repeat_radius": 5,
    "empty_repeat_step": 0.75,
    "empty_repeat_cap": 4.0,
}
