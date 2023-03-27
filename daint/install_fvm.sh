#!/bin/bash -l

BRANCH=${BRANCH:-distributed}

. prepare_fvm.sh
. prepare_mpi.sh
pushd "$FVM" || return
ENABLE_DISTRIBUTED=1 \
  ENABLE_GPU=1 \
  CUPY=cupy-cuda112 \
  INSTALL_PRE_COMMIT=0 \
  MPICC=cc \
  MPICXX=CC \
  VENV=venv \
  FRESH_INSTALL=1 \
  INSTALL_PARALLEL_HDF5=1 \
  INSTALL_PARALLEL_NETCDF=1 \
  . bootstrap_venv.sh
popd || return
