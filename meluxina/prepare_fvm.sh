#!/bin/bash -l

BRANCH=${BRANCH:-distributed}

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
module load OpenMPI/4.1.4-GCC-11.3.0
module load Python

# set/fix CUDA-related variables
#NVCC_PATH=$(which nvcc)
#CUDA_PATH=$(echo $NVCC_PATH | sed -e "s/\/bin\/nvcc//g")
#export CUDA_HOME=$CUDA_PATH
#export NVHPC_CUDA_HOME=$CUDA_PATH
#export NVHPC_CUDA_LIB_PATH=/apps/USE/easybuild/release/2022.1/software/NVHPC/22.7-CUDA-11.7.0/Linux_x86_64/22.7/compilers/lib
#export LD_LIBRARY_PATH="${LD_LIBRARY_PATH/${NVHPC_CUDA_LIB_PATH}:/}"

# set path to FVM code
export FVM="$SCRATCH"/fvm-gt4py/"$BRANCH"
export GT_CACHE_ROOT=$FVM/gt_cache
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf
