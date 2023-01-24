#!/bin/bash -l

set -a

BRANCH=distributed-dev
GT_BACKEND_L=( gt:cpu_kfirst dace:gpu )
NUM_NODES_L=( 1 2 4 8 16 32 64 128 256 512 1024 )
NUM_RUNS=5
NUM_THREADS=12
NUMPY_DTYPE_L=( float64 )
OVERCOMPUTING_L=( 0 )
TIME=01:00:00
USE_CASE_L=( thermal-large thermal-large-order3 )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
    for NUMPY_DTYPE in "${NUMPY_DTYPE_L[@]}"; do
      for OVERCOMPUTING in "${OVERCOMPUTING_L[@]}"; do
        for NUM_NODES in "${NUM_NODES_L[@]}"; do
          JOB_NAME="$USE_CASE-$GT_BACKEND-$NUMPY_DTYPE-$OVERCOMPUTING-$NUM_NODES" \
            JOB_SCRIPT=run_fvm.sh \
            . submit.sh
        done
      done
    done
  done
done

set +a