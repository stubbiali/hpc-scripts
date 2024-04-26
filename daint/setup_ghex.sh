#!/bin/bash

module purge -f
module load PrgEnv-gnu
module load daint-gpu

. /users/subbiali/spack/share/spack/setup-env.sh
spack env activate ghex-dev

spack load boost
boost_root=$(spack location -i boost)
export BOOST_ROOT="$boost_root"

spack load cmake

spack load cuda
cuda_home=$(spack location -i cuda)
export CUDA_HOME="$cuda_home"

spack load mpich
mpich_home=$(spack location -i mpich)
export CC="$mpich_home"/bin/mpicc
export CXX="$mpich_home"/bin/mpicxx
export MPICC="$mpich_home"/bin/mpicc
export MPICXX="$mpich_home"/bin/mpicxx

spack load python
