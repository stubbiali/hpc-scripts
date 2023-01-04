#!/bin/bash -l

BRANCH=${BRANCH:-distributed}
ENV=${ENV:-gnu}
GT_BACKEND=${GT_BACKEND:-gt:cpu_kfirst}
MPI=${MPI:-none}
NUM_NODES=${NUM_NODES:-1}
NUM_RUNS=${NUM_RUNS:-5}
NUM_TASKS_PER_NODE=${NUM_TASKS_PER_NODE:-1}
NUM_THREADS=${NUM_THREADS:-}
OVERCOMPUTING=${OVERCOMPUTING:-0}
USE_CASE=${USE_CASE:-thermal}

if [ "$MPI" = "none" ]; then
  VENV=venv/"$ENV"
else
  VENV=venv/"$ENV"-"$MPI"
fi

NUM_TASKS=$(( NUM_TASKS_PER_NODE * NUM_NODES ))
CPUS_PER_TASK=$(( 256 / NUM_TASKS_PER_NODE ))
if [ -z "$NUM_THREADS" ]; then
  NUM_THREADS=$(( 128 / NUM_TASKS_PER_NODE ))
fi

. prepare_fvm.sh
pushd "$FVM" || return
. "$VENV"/bin/activate
pushd drivers || return

for i in $(eval echo "{1..$NUM_RUNS}"); do
  echo "NUM_NODES=$NUM_NODES: start"
  GT_BACKEND="$GT_BACKEND" \
    FVM_ENABLE_BENCHMARKING=1 \
    FVM_ENABLE_OVERCOMPUTING="$OVERCOMPUTING" \
    GHEX_NUM_COMMS=1 \
    GHEX_MAX_NUM_FIELDS_PER_COMM=13 \
    OMP_NUM_THREADS="$NUM_THREADS" \
    OMP_PLACES=cores \
    OMP_PROC_BIND=close \
    srun \
      --cpus-per-task="$CPUS_PER_TASK" \
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
