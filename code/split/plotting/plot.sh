#!/bin/bash
# python3 compute_mem_usage.py && python3 ccompute_policy_results.py
python3 plot_many.py && python3 plot_dropped.py && python3 plot_run_across_mem.py && python3 plot_mem_usage.py && python3 plot_cold_across_mem.py && python3 plot_cold_percent.py