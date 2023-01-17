#!/bin/bash -l

BRANCH=${BRANCH:-distributed}
MPI=${MPI:-none}
PREFIX=${PREFIX:-nasu}

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

# load and configure performance analysis tools
module load Score-P/7.1-gompi-2022a-CUDA-11.7.0
export SCOREP_CUDA_ENABLE=yes
export SCOREP_ENABLE_PROFILING=true
export SCOREP_ENABLE_TRACING=true
export SCOREP_PROFILING_MAX_CALLPATH_DEPTH=1000
export SCOREP_TOTAL_MEMORY=1G

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
export FVM="$SCRATCH"/"$PREFIX"/fvm-gt4py/"$BRANCH"
export GT_CACHE_ROOT="$FVM"/gt_cache
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf
