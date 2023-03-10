#!/bin/bash -l

BRANCH=${BRANCH:-distributed}
GHEX_PREFIX=${GHEX_PREFIX:-}
GT_BACKEND=${GT_BACKEND:-gt:cpu_kfirst}
NUM_NODES=${NUM_NODES:-1}
NUM_RUNS=${NUM_RUNS:-1}
NUM_THREADS=${NUM_THREADS:-12}
OVERCOMPUTING=${OVERCOMPUTING:-0}
USE_CASE=${USE_CASE:-thermal}
VENV=venv

. prepare_fvm.sh
. prepare_mpi.sh
pushd "$FVM" || return
. "$VENV"/bin/activate
pushd drivers || return
for i in $(eval echo "{1..$NUM_RUNS}"); do
  echo "NUM_NODES=$NUM_NODES, i=$i: start"
  FVM_ENABLE_BENCHMARKING=1 \
    FVM_ENABLE_OVERCOMPUTING="$OVERCOMPUTING" \
    GHEX_PREFIX="$GHEX_PREFIX" \
    GHEX_NUM_COMMS=1 \
    GHEX_MAX_NUM_FIELDS_PER_COMM=13 \
    GT_BACKEND="$GT_BACKEND" \
    OMP_NUM_THREADS="$NUM_THREADS" \
    srun -N "$NUM_NODES" -n "$NUM_NODES" \
    python run_model.py \
      ../config/weak-scaling/"$USE_CASE"/"$NUM_NODES".yml \
      --csv-file=../data/daint/weak-scaling/"$USE_CASE"/"$NUM_NODES".csv
  echo "NUM_NODES=$NUM_NODES, i=$i: end"
  echo ""
done
popd || return
popd || return
