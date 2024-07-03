#!/bin/bash -l

BRANCH=${BRANCH:-main}
ENV=${ENV:-gnu}  # options: amd, cray, gnu
PARTITION=${PARTITION:-standard-g}  # options: dev, dev-g, standard, standard-g
STACK=${STACK:-lumi}  # options: cray, lumi

# unload all modules
module purge

# load software stack
if [ "$STACK" = "cray" ]; then
  module load CrayEnv
elif [ "$STACK" = "lumi" ]; then
  module load LUMI/22.08
else
  echo "Unknown software stack '$ENV'."
  return
fi

# load partition
case $PARTITION in
  dev|standard)
    module load partition/C
    SUFFIX="-host" ;;
  dev-g|standard-g)
    module load partition/G
    SUFFIX="" ;;
  *)
    echo "Unknown partition '$PARTITION'."
    return ;;
esac

# load env
if [ "$ENV" = "amd" ]; then
  module load PrgEnv-amd
  CPE=cpeAMD
elif [ "$ENV" = "cray" ]; then
  module load PrgEnv-cray
  CPE=cpeCray
elif [ "$ENV" = "gnu" ]; then
  module load PrgEnv-gnu
  CPE=cpeGNU

    # load most recent gcc
#    module load gcc/11.2.0
#    export LD_LIBRARY_PATH=/usr/local/apps/gcc/11.2.0/lib64:$LD_LIBRARY_PATH
else
  echo "Unknown env '$ENV'."
  return
fi

# load tools and libraries
module load Boost/1.79.0-"$CPE"-22.08
module load buildtools
#module load cray-hdf5-parallel
#module load cray-netcdf-hdf5parallel
module load cray-python
#module load gcc
case $PARTITION in
  dev-g|standard-g)
    module load rocm ;;
  *) ;;
esac

# set path to FVM code
export FVM="$PROJECT"/fvm-gt4py/"$BRANCH"
export GT_CACHE_ROOT="$PROJECT"/fvm-gt4py/gt_cache/"$ENV""$SUFFIX"
export GT_CACHE_DIR_NAME=.gt_cache
export DACE_CONFIG="$GT_CACHE_ROOT"/.dace.conf

# patch PYTHONPATH
export PYTHONPATH=/opt/cray/pe/python/3.9.12.1

# set/fix HIP-related variables
case $PARTITION in
  dev-g|standard-g)
    export CUDA_HOME=/opt/rocm  # required by GT4Py
    export CUPY_INSTALL_USE_HIP=1
    export GT4PY_USE_HIP=1
    export HCC_AMDGPU_TARGET=gfx90a
    export ROCM_HOME=/opt/rocm
    ;;
esac

# expose compiler wrappers
#export CC=cc CXX=CC CUDA_HOST_CXX=CC

# path to custom build of HDF5 and NetCDF-C
export HDF5_ROOT="$PROJECT"/hdf5/1.14.1-2/build/"$ENV""$SUFFIX"
export NETCDF_ROOT="$PROJECT"/netcdf-c/4.9.2/build/"$ENV""$SUFFIX"

# low-level GT4Py, DaCe and GHEX config
export DACE_DEFAULT_BLOCK_SIZE=128,1,1
export GHEX_BUILD_PREFIX="$ENV""$SUFFIX"

# MPICH options
export MPICH_CRAY_OPT_THREAD_SYNC=1
export MPICH_GNI_USE_UNASSIGNED_CPUS=enabled
export MPICH_MAX_THREAD_SAFETY=multiple
export MPICH_NEMESIS_ASYNC_PROGRESS=MC
export MPICH_NEMESIS_ON_NODE_ASYNC_OPT=1
export MPICH_OPTIMIZED_MEMCPY=2
case $PARTITION in
  dev|standard)
    export MPICH_GPU_SUPPORT_ENABLED=0 ;;
  dev-g|standard-g)
    export MPICH_GPU_SUPPORT_ENABLED=1
    export MPICH_RDMA_ENABLED_CUDA=1
    ;;
esac
