#!/bin/bash -l

ENV_L=( gnu )
GT_BACKEND_L=( gt:cpu_kfirst )
MPI_L=( openmpi intel hpcx )
NUM_NODES_L=( 1 2 4 8 16 32 64 128 )
NUM_RUNS=${NUM_RUNS:-8}
NUM_TASKS_PER_NODE=${NUM_TASKS_PER_NODE:-1}
TIME=${TIME:-01:00:00}
USE_CASE_L=( baroclinic-wave-sphere thermal )

for USE_CASE in "${USE_CASE_L[@]}"; do
  for ENV in "${ENV_L[@]}"; do
    for MPI in "${MPI_L[@]}"; do
      for GT_BACKEND in "${GT_BACKEND_L[@]}"; do
        for NUM_NODES in "${NUM_NODES_L[@]}"; do
          NUM_TASKS=$(( NUM_NODES * NUM_TASKS_PER_NODE ))
          JOB_NAME="$USE_CASE-$ENV-$MPI-$NUM_NODES" \
            JOB_SCRIPT=run_fvm.sh \
            NUM_THREADS=64 \
            . submit.sh
        done
      done
    done
  done
done

