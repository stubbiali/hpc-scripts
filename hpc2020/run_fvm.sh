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
PRECISION=${PRECISION:-double}
PYTHON3_MINOR_VERSION=${PYTHON3_MINOR_VERSION:-10}
USE_CASE=${USE_CASE:-thermal}

if [ "$MPI" = "none" ]; then
  PREFIX=py3"$PYTHON3_MINOR_VERSION"/"$ENV"
else
  PREFIX=py3"$PYTHON3_MINOR_VERSION"/"$ENV"/"$MPI"
fi

NUM_TASKS=$(( NUM_TASKS_PER_NODE * NUM_NODES ))
CPUS_PER_TASK=$(( 256 / NUM_TASKS_PER_NODE ))
if [ -z "$NUM_THREADS" ]; then
  NUM_THREADS=$(( 128 / NUM_TASKS_PER_NODE ))
fi

. prepare_fvm.sh
pushd "$FVM" || return
. venv/"$PREFIX"/bin/activate
pushd drivers || return

mkdir -p ../data/hpc2020/"$PREFIX"/weak-scaling/"$USE_CASE"

for i in $(eval echo "{1..$NUM_RUNS}"); do
  echo "NUM_NODES=$NUM_NODES: start"
  FVM_ENABLE_BENCHMARKING=1 \
    FVM_ENABLE_OVERCOMPUTING="$OVERCOMPUTING" \
    FVM_NUMPY_DTYPE="$NUMPY_DTYPE" \
    GHEX_NUM_COMMS=1 \
    GHEX_AGGREGATE_FIELDS=1 \
    GT_BACKEND="$GT_BACKEND" \
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
        --performance-data-file=../data/hpc2020/"$PREFIX"/weak-scaling/"$USE_CASE"/"$NUM_TASKS".csv
  echo "NUM_NODES=$NUM_NODES, i=$i.1: end"
  echo ""
done

popd || return
popd || return
