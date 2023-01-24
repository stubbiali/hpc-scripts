#!/bin/bash -l

set -a

ACCOUNT=p200061
BRANCH=distributed-dev
ENV=gnu
GT_BACKEND_L=( gt:cpu_kfirst )
JOB_SCRIPT=run_fvm_cpu.sh
MPI_L=( openmpi )
NUM_NODES_L=( 4 8 16 32 )
NUM_RUNS=4
NUM_TASKS_PER_NODE=2
NUM_THREADS=32
NUMPY_DTYPE_L=( float64 )
OVERCOMPUTING_L=( 0 1 )
TIME=01:00:00
USE_CASE_L=( thermal-large )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for MPI in "${MPI_L[@]}"; do
    for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
      for NUMPY_DTYPE in "${NUMPY_DTYPE_L[@]}"; do
        for OVERCOMPUTING in "${OVERCOMPUTING_L[@]}"; do
          for NUM_NODES in "${NUM_NODES_L[@]}"; do
            NUM_TASKS=$(( NUM_NODES * NUM_TASKS_PER_NODE ))
            JOB_NAME="$USE_CASE-$MPI-$GT_BACKEND-$NUMPY_DTYPE-$OVERCOMPUTING-$NUM_NODES-$NUM_TASKS" \
              . submit.sh
          done
        done
      done
    done
  done
done

set +a
