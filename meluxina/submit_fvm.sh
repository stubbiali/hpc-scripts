#!/bin/bash -l

set -a

BRANCH=${BRANCH:-distributed}
GT_BACKEND_L=( gt:cpu_kfirst )
JOB_SCRIPT=run_fvm_cpu.sh
NUM_NODES_L=( 1 2 )
NUM_RUNS=4
NUM_TASKS_PER_NODE=2
OVERCOMPUTING_L=( 0 )
TIME=${TIME:-01:00:00}
USE_CASE_L=( thermal-large )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
    for OVERCOMPUTING_L in "${OVERCOMPUTING_L[@]}"; do
      for NUM_NODES in "${NUM_NODES_L[@]}"; do
        NUM_TASKS=$(( NUM_NODES * NUM_TASKS_PER_NODE ))
        JOB_NAME="$USE_CASE-$NUM_NODES-$NUM_TASKS" \
          . submit.sh
      done
    done
  done
done

set +a
