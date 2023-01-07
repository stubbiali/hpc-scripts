#!/bin/bash

BRANCH=${BRANCH:-main}

module purge

module load daint-gpu
module load Boost
module load cray-hdf5-parallel
module load cray-netcdf-hdf5parallel
module load cray-python
module load CMake
module load cudatoolkit/11.2.0_3.39-2.1__gf93aa1c

NVCC_PATH=$(which nvcc)
CUDA_PATH=$(echo $NVCC_PATH | sed -e "s/\/bin\/nvcc//g")
export CUDA_HOME=$CUDA_PATH
export LD_LIBRARY_PATH=$CUDA_PATH/lib64:$LD_LIBRARY_PATH

export FVM=$SCRATCH/fvm-gt4py/"$BRANCH"
export GT_CACHE_ROOT=$FVM/gt_cache
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG=$GT_CACHE_ROOT/.dace.conf
