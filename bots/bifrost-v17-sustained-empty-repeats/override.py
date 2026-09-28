"""Bifröst v17: wait for persistent repeats before discouraging empty routes."""
OVERRIDE = {
    "empty_repeat_threshold": 10,
    "empty_repeat_radius": 5,
    "empty_repeat_step": 0.75,
    "empty_repeat_cap": 4.0,
}
