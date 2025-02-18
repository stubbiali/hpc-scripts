#!/bin/bash -l

BRANCH=${BRANCH:-main}
ENV=${ENV:-gnu}

# unload all modules
module purge

# load env
if [ "$ENV" = "gnu" ]; then
    module load prgenv/gnu

    # load most recent gcc
    module load gcc/11.2.0
elif [ "$ENV" = "intel" ]; then
    module load prgenv/intel
elif [ "$ENV" = "amd" ]; then
    module load prgenv/amd
else
    echo "Unknown env '$ENV'."
    return
fi

# load tools and libraries
module load boost
module load cmake
module load hdf5
module load netcdf4
module load nvidia/22.11
module load python3

# set/fix CUDA-related variables
NVCC_PATH=$(which nvcc)
CUDA_PATH=$(echo "$NVCC_PATH" | sed -e "s/\/bin\/nvcc//g")
export CUDA_HOME="$CUDA_PATH"
export NVHPC_CUDA_HOME="$CUDA_PATH"

# set path to cloudsc code
export CLOUDSC="$SCRATCH"/cloudsc/"$BRANCH"
export GT_CACHE_ROOT="$CLOUDSC"/gt_cache/"$ENV"
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf

# required to run OpenACC version (w/o hoisting) on large domains
export PGI_ACC_CUDA_HEAPSIZE=8GB
