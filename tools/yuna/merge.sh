#!/bin/bash
# merge cloud + staged VM results into $E/all.jsonl
E=/home/claude/repo/experiment_data/temporal_policy_20260927T173800Z_yuna
cat $E/results.jsonl /mnt/user-data/uploads/UNSW-Battlecode-2026/experiment_data/temporal_policy_20260927T173800Z_yuna/results_vm.jsonl 2>/dev/null > $E/all.jsonl
wc -l < $E/all.jsonl
