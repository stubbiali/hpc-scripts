#!/bin/bash -l

BRANCH=distributed
ENV_L=( gnu )
MPI_L=( openmpi hpcx )

mkdir -p fvm-gt4py/"$BRANCH"/venv

for ENV in "${ENV_L[@]}"; do
  for MPI in "${MPI_L[@]}"; do
    . prepare_fvm.sh
    pushd "$FVM" || return
    ENABLE_DISTRIBUTED=1 \
      ENABLE_GPU=0 \
      GHEX_PREFIX="$MPI" \
      INSTALL_PRE_COMMIT=0 \
      MPICC=mpicc \
      MPICXX=mpicxx \
      VENV=venv/"$ENV"-"$MPI" \
      . bootstrap_venv.sh
    popd || return
  done
done
