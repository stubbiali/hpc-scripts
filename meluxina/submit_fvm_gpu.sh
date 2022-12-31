#!/bin/bash -l

set -a

BRANCH=${BRANCH:-distributed}
GT_BACKEND_L=( dace:gpu )
NUM_NODES_L=( 1 2 )
NUM_RUNS=${NUM_RUNS:-8}
NUM_TASKS_PER_NODE=${NUM_TASKS_PER_NODE:-4}
OVERCOMPUTING_L=( 0 )
TIME=${TIME:-01:00:00}
USE_CASE_L=( thermal-large-periodic baroclinic-wave-sphere baroclinic-wave-sphere-unsplit )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
    for OVERCOMPUTING_L in "${OVERCOMPUTING_L[@]}"; do
      for NUM_NODES in "${NUM_NODES_L[@]}"; do
        NUM_TASKS=$(( NUM_NODES * NUM_TASKS_PER_NODE ))
        JOB_NAME="$USE_CASE-$NUM_NODES-$NUM_TASKS" \
          JOB_SCRIPT=run_fvm_gpu.sh \
          . submit.sh
      done
    done
  done
done

set +a
