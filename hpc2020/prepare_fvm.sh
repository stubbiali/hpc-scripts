#!/bin/bash -l

BRANCH=${BRANCH:-main}
ENV=${ENV:-gnu}
MPI=${MPI:-none}
PYTHON3_MINOR_VERSION=${PYTHON3_MINOR_VERSION:-8}

# unload all modules
module purge

# load env
if [ "$ENV" = "gnu" ]; then
    module load prgenv/gnu

    # load most recent gcc
    module load gcc/11.2.0
    export LD_LIBRARY_PATH=/usr/local/apps/gcc/11.2.0/lib64:$LD_LIBRARY_PATH
elif [ "$ENV" = "intel" ]; then
    module load prgenv/intel
elif [ "$ENV" = "amd" ]; then
    module load prgenv/amd
else
    echo "Unknown env '$ENV'."
    return
fi

# load python interpreter
if [ "$PYTHON3_MINOR_VERSION" = "8" ]; then
    module load python3/3.8.8-01
elif [ "$PYTHON3_MINOR_VERSION" = "10" ]; then
    module load python3/3.10.10-01
else
    echo "Python 3.$PYTHON3_MINOR_VERSION not available."
    return
fi

# load tools and libraries
module load boost
module load cmake
module load hdf5
module load netcdf4
module load nvidia/22.11

# load MPI
if [ "$MPI" = "openmpi" ]; then
    module load openmpi
elif [ "$MPI" = "intel" ]; then
    module load intel-mpi
elif [ "$MPI" = "hpcx" ]; then
    module load hpcx-openmpi/2.10.0
elif [ "$MPI" != "none" ]; then
    echo "Unknown MPI installation '$MPI'."
    return
fi

# set/fix CUDA-related variables
NVCC_PATH=$(which nvcc)
CUDA_PATH=$(echo "$NVCC_PATH" | sed -e "s/\/bin\/nvcc//g")
export CUDA_HOME="$CUDA_PATH"
export NVHPC_CUDA_HOME="$CUDA_PATH"

# set path to FVM code
ROOT="$PWD"
export FVM="$ROOT"/fvm-gt4py/"$BRANCH"
export GT_CACHE_ROOT="$ROOT"/fvm-gt4py/gt_cache/"$ENV"
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf
export GHEX_BUILD_PREFIX=py3"$PYTHON3_MINOR_VERSION"/"$ENV"/"$MPI"
