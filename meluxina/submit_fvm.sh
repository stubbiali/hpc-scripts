#!/bin/bash -l

set -a

ACCOUNT=p200061
BRANCH=distributed
NUMPY_DTYPE=float64
GT_BACKEND_L=( gt:gpu )
JOB_SCRIPT=run_fvm_gpu.sh
MPI=openmpi
NUM_NODES_L=( 1 2 4 8 16 )
NUM_RUNS=4
NUM_TASKS_PER_NODE=4
TIME=01:00:00
USE_CASE_L=( thermal-large thermal-large-order3 )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
    for NUM_NODES in "${NUM_NODES_L[@]}"; do
      NUM_TASKS=$(( NUM_NODES * NUM_TASKS_PER_NODE ))
      JOB_NAME="$USE_CASE-$NUM_NODES-$NUM_TASKS" \
        . submit.sh
    done
  done
done

set +a
