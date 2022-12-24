#!/bin/bash -l

BRANCH=${BRANCH:-distributed-dev}
ENV=${ENV:-gnu}
GT_BACKEND=${GT_BACKEND:-gt:cpu_kfirst}
MPI=${MPI:-openmpi}
NUM_NODES=${NUM_NODES:-1}
NUM_RUNS=${NUM_RUNS:-5}
NUM_TASKS=${NUM_TASKS:-1}
NUM_THREADS=${NUM_THREADS:-12}
OVERCOMPUTING=${OVERCOMPUTING:-0}
USE_CASE=${USE_CASE:-thermal}

VENV=venv/"$ENV"-"$MPI"
if [ "$NUM_TASKS" -gt "$NUM_NODES" ]; then
  NUM_TASKS_PER_NODE=2
else
  NUM_TASKS_PER_NODE=1
fi

. prepare_fvm.sh
pushd "$FVM" || return
. "$VENV"/bin/activate
pushd drivers || return

for i in $(eval echo "{1..$NUM_RUNS}"); do
  echo "NUM_NODES=$NUM_NODES: start"
  GT_BACKEND="$GT_BACKEND" \
    FVM_ENABLE_BENCHMARKING=1 \
    GHEX_NUM_COMMS=1 \
    GHEX_MAX_NUM_FIELDS_PER_COMM=13 \
    FVM_ENABLE_OVERCOMPUTING="$OVERCOMPUTING" \
    OMP_NUM_THREADS="$NUM_THREADS" \
    OMP_PLACES=cores \
    OMP_PROC_BIND=spread \
    srun \
      --cpus-per-task=256 \
      --nodes="$NUM_NODES" \
      --ntasks="$NUM_TASKS" \
      --ntasks-per-node="$NUM_TASKS_PER_NODE" \
      python run_model.py \
        ../config/weak-scaling/"$USE_CASE"/"$NUM_TASKS".yml \
        --csv-file=../data/hpc2020/weak-scaling/"$USE_CASE"/"$ENV"/"$MPI"/"$NUM_TASKS".csv
  echo "NUM_NODES=$NUM_NODES, i=$i.1: end"
  echo ""
done

popd || return
popd || return
