#!/bin/bash -l

BRANCH=${BRANCH:-distributed}
GT_BACKEND=${GT_BACKEND:-dace:gpu}
NUM_NODES=${NUM_NODES:-1}
NUM_RUNS=${NUM_RUNS:-5}
NUM_TASKS=${NUM_TASKS:-1}
OVERCOMPUTING=${OVERCOMPUTING:-0}
USE_CASE=${USE_CASE:-thermal}

#if [ "$NUM_TASKS" -gt "$NUM_NODES" ]; then
#  NUM_TASKS_PER_NODE=2
#else
#  NUM_TASKS_PER_NODE=1
#fi

. prepare_fvm.sh
pushd "$FVM" || return
. venv/bin/activate
pushd drivers || return

export OMPI_MCA_btl_openib_want_cuda_gdr=1
export UCX_MAX_RNDV_RAILS=1

for i in $(eval echo "{1..$NUM_RUNS}"); do
  echo "NUM_NODES=$NUM_NODES: start"
  GT_BACKEND="$GT_BACKEND" \
    FVM_ENABLE_BENCHMARKING=1 \
    FVM_ENABLE_OVERCOMPUTING="$OVERCOMPUTING" \
    GHEX_NUM_COMMS=1 \
    GHEX_MAX_NUM_FIELDS_PER_COMM=13 \
    srun \
      --nodes="$NUM_NODES" \
      --ntasks="$NUM_TASKS" \
      --ntasks-per-node="$NUM_TASKS_PER_NODE" \
      --gpus-per-task=1 \
      python run_model.py \
        ../config/weak-scaling/"$USE_CASE"/"$NUM_TASKS".yml \
        --csv-file=../data/meluxina/weak-scaling/"$USE_CASE"/"$NUM_TASKS".csv
  echo "NUM_NODES=$NUM_NODES, i=$i.1: end"
  echo ""
done

popd || return
popd || return
