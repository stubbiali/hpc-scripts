#!/bin/bash -l

BRANCH=${BRANCH:-distributed}
MPI=${MPI:-none}

# unload all modules
module purge --force

# load env
module load env/release/2022.1

# load compilers and libraries
module load GCC
module load CUDA/11.7.0

# load tools
module load Boost
module load CMake
module load netCDF
module load Python

# load MPI
if [ "$MPI" = "openmpi" ]; then
  module load OpenMPI/4.1.4-GCC-11.3.0
elif [ "$MPI" = "hpcx" ]; then
    module load HPCX
elif [ "$MPI" != "none" ]; then
    echo "Unknown MPI installation '$MPI'."
    return
fi

# set path to FVM code
export FVM=/project/scratch/p200061/nasu/fvm-gt4py/"$BRANCH"
export GT_CACHE_ROOT="$FVM"/gt_cache
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf
