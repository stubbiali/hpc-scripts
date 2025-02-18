#!/bin/bash -l

BRANCH=${BRANCH:-distributed}
ENV=${ENV:-gnu}
GT_BACKEND=${GT_BACKEND:-gt:cpu_kfirst}
MPI=${MPI:-openmpi}
NUM_NODES=${NUM_NODES:-1}
NUM_RUNS=${NUM_RUNS:-5}
NUM_TASKS_PER_NODE=${NUM_TASKS_PER_NODE:-1}
NUM_THREADS=${NUM_THREADS:-64}
NUMPY_DTYPE=${NUMPY_DTYPE:-float64}
OVERCOMPUTING=${OVERCOMPUTING:-0}
USE_CASE=${USE_CASE:-thermal}

CPUS_PER_TASK=$(( 128 / NUM_TASKS_PER_NODE ))
NUM_TASKS=$(( NUM_NODES * NUM_TASKS_PER_NODE ))

. prepare_fvm.sh
pushd "$FVM" || return
. venv/"$ENV"-"$MPI"/bin/activate
pushd drivers || return

export OMP_NUM_THREADS="$NUM_THREADS"
if [ "$ENV" = "gnu" ]; then
  export OMP_PLACES=cores
  export OMP_PROC_BIND=close
  export OMP_DISPLAY_AFFINITY=true
elif [ "$ENV" = "intel" ]; then
  export KMP_HW_SUBSET=2s,16c,1t
  export KMP_AFFINITY=compact,verbose
fi

mkdir -p ../data/meluxina/weak-scaling/"$USE_CASE"/"$ENV"/"$MPI"

for i in $(eval echo "{1..$NUM_RUNS}"); do
  echo "i=$i: start"
  FVM_ENABLE_BENCHMARKING=1 \
    FVM_ENABLE_OVERCOMPUTING="$OVERCOMPUTING" \
    FVM_NUMPY_DTYPE="$NUMPY_DTYPE" \
    GHEX_NUM_COMMS=1 \
    GHEX_MAX_NUM_FIELDS_PER_COMM=13 \
    GHEX_BUILD_PREFIX="$MPI" \
    GT_BACKEND="$GT_BACKEND" \
    srun \
      --nodes="$NUM_NODES" \
      --ntasks="$NUM_TASKS" \
      --ntasks-per-node="$NUM_TASKS_PER_NODE" \
      --cpus-per-task="$CPUS_PER_TASK" \
      python run_model.py \
        ../config/weak-scaling/"$USE_CASE"/"$NUM_TASKS".yml \
        --performance-data-file=../data/meluxina/weak-scaling/"$USE_CASE"/"$ENV"/"$MPI"/"$NUM_TASKS".csv
  echo "i=$i: end"
  echo ""
done

popd || return
popd || return
