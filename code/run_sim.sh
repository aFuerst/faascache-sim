#!/bin/bash

#logdir='/data2/alfuerst/verify-test/logs'
#memstep=3000
#numfuncs=392
#savedir='/data2/alfuerst/verify-test'
#tracedir='/data2/alfuerst/azure/functions/trace_pckl/represent'
trace_dir="/data2/alfuerst/azure/functions/trace_pckl/precombined"
trace_output_dir="/data2/alfuerst/verify-test"
log_dir="$trace_output_dir/logs"
memory_dir="$trace_output_dir/memory"
analyzed_dir="$trace_output_dir/analyzed"
plot_dir="/home/alfuerst/repos/faas-keepalive-20/code/split/figs/test/"
num_funcs=392

# paper used 500 simulation, but 3000 is used here for faster results
memstep=3000

# download trace

# run simulation
python3 ./split/many_run.py --tracedir $trace_dir --numfuncs $num_funcs --savedir $trace_output_dir --logdir $log_dir --memstep=$memstep

# analyze results

python3 ./split/plotting/compute_mem_usage.py --logdir $log_dir --savedir $memory_dir
python3 ./split/plotting/compute_policy_results.py --pckldir $trace_output_dir --savedir $analyzed_dir

# plot graphs

# python3 ./split/plotting/plot_many.py
# python3 ./split/plotting/plot_dropped.py
python3 ./split/plotting/plot_run_across_mem.py --analyzeddir $analyzed_dir --plotdir $plot_dir --numfuncs $num_funcs
# python3 ./split/plotting/plot_mem_usage.py
python3 ./split/plotting/plot_cold_across_mem.py --analyzeddir $analyzed_dir --plotdir $plot_dir --numfuncs $num_funcs
# python3 ./split/plotting/plot_cold_percent.py

