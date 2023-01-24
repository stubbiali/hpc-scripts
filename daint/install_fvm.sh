#!/bin/bash -l

BRANCH=distributed-dev

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
  . bootstrap_venv.sh
popd || return
