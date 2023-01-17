#!/bin/bash -l

set -a

BRANCH=distributed
ENV_L=( gnu )
GT_BACKEND_L=( gt:cpu_kfirst )
MPI_L=( hpcx )
NUM_NODES_L=( 1 2 )
NUM_RUNS=4
NUM_TASKS_PER_NODE=2
NUM_THREADS=64
NUMPY_DTYPE=float64
TIME=01:00:00
USE_CASE_L=( thermal-large thermal-large-order3 )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for ENV in "${ENV_L[@]}"; do
    for MPI in "${MPI_L[@]}"; do
      for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
        for NUM_NODES in "${NUM_NODES_L[@]}"; do
          JOB_NAME="$USE_CASE-$ENV-$MPI-$NUMPY_DTYPE-$NUM_NODES" \
            JOB_SCRIPT=run_fvm.sh \
            NUM_TASKS=$(( NUM_TASKS_PER_NODE * NUM_NODES )) \
            . submit.sh
        done
      done
    done
  done
done

set +a
