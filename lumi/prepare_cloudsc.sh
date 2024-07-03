#!/bin/bash -l

BRANCH=${BRANCH:-develop}
ENV=${ENV:-gnu} # options: amd, cray, gnu
STACK=${STACK:-lumi}  # options: cray, lumi

# unload all modules
module --force purge

# load software stack
if [ "$STACK" = "cray" ]; then
    module load CrayEnv partition/G
elif [ "$STACK" = "lumi" ]; then
    module load LUMI/22.08 partition/G
else
    echo "Unknown software stack '$ENV'."
    return
fi

# load programming environment
if [ "$ENV" = "amd" ]; then
    module load PrgEnv-amd
    SUFFIX=cpeAMD-22.08
elif [ "$ENV" = "cray" ]; then
    module load PrgEnv-cray
    SUFFIX=cpeCray-22.08
elif [ "$ENV" = "gnu" ]; then
    module load PrgEnv-gnu
    SUFFIX=cpeGNU-22.08
else
    echo "Unknown programming environment '$ENV'."
    return
fi

# load tools and libraries
module load Boost/1.79.0-"$SUFFIX"
module load buildtools/22.08
#module load CMake/3.24.0  # error: module exists but cannot be loaded
module load cray-hdf5/1.12.1.5
module load cray-python/3.9.12.1
module load git/2.37.2
#module load make/4.4.1  # error: module exists but cannot be loaded
module load rocm/5.2.3

# set/fix ROCm-related variables
export __HIP_PLATFORM_HCC__
export CUDA_HOME=/opt/rocm
export CUPY_INSTALL_USE_HIP=1
export GT4PY_USE_HIP=1
export HCC_AMDGPU_TARGET=gfx90a
export ROCM_HOME=/opt/rocm

# patch PYTHONPATH
export PYTHONPATH=/opt/cray/pe/python/3.9.12.1

# set path to cloudsc code
export CLOUDSC="$PROJECT"/cloudsc/"$BRANCH"
export GT_CACHE_ROOT="$CLOUDSC"/src/cloudsc_gt4py/gt_cache/"$ENV"
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf

# required to run OpenACC version (w/o hoisting) on large domains
#export PGI_ACC_CUDA_HEAPSIZE=8GB
