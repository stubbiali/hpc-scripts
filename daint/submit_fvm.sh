#!/bin/bash -l

set -a

BRANCH=distributed
GT_BACKEND_L=( gt:cpu_kfirst )
NUM_NODES_L=( 1 2 4 8 16 32 64 128 256 512 1024 )
NUM_RUNS=8
NUM_THREADS=12
OVERCOMPUTING_L=( 0 )
TIME=01:00:00
USE_CASE_L=( thermal-large thermal-large-periodic baroclinic-wave-sphere baroclinic-wave-sphere-unsplit )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
    for OVERCOMPUTING_L in "${OVERCOMPUTING_L[@]}"; do
      for NUM_NODES in "${NUM_NODES_L[@]}"; do
        JOB_NAME="$USE_CASE-$NUM_NODES" \
          JOB_SCRIPT=run_fvm.sh \
          . submit.sh
      done
    done
  done
done

set +a