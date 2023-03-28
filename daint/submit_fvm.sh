#!/bin/bash -l

set -a

ACCOUNT=s299
BRANCH=distributed
GT_BACKEND_L=( gt:cpu_kfirst dace:gpu )
NUM_NODES_L=( 1 2 4 8 16 32 64 128 256 512 1024 2048 )
NUM_RUNS=10
NUM_THREADS=12
PRECISION_L=( double single )
OVERCOMPUTING_L=( 0 )
TIME=01:00:00
USE_CASE_L=( supercell )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
    for PRECISION in "${PRECISION_L[@]}"; do
      for OVERCOMPUTING in "${OVERCOMPUTING_L[@]}"; do
        for NUM_NODES in "${NUM_NODES_L[@]}"; do
          JOB_NAME="$BRANCH-$USE_CASE-$GT_BACKEND-$PRECISION-$OVERCOMPUTING-$NUM_NODES" \
            JOB_SCRIPT=run_fvm.sh \
            . submit.sh
        done
      done
    done
  done
done

set +a