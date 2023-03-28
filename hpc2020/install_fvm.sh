#!/bin/bash -l

BRANCH=distributed
ENV_L=( gnu )
MPI_L=( hpcx )
PYTHON3_MINOR_VERSION_L=( 10 )

ROOT="$PWD"
mkdir -p fvm-gt4py/"$BRANCH"/venv

for ENV in "${ENV_L[@]}"; do
  for MPI in "${MPI_L[@]}"; do
    for PYTHON3_MINOR_VERSION in "${PYTHON3_MINOR_VERSION_L[@]}"; do
      if [ "$MPI" = "none" ]; then
        PREFIX=py3"$PYTHON3_MINOR_VERSION"/"$ENV"
        ENABLE_DISTRIBUTED=0
      else
        PREFIX=py3"$PYTHON3_MINOR_VERSION"/"$ENV"/"$MPI"
        ENABLE_DISTRIBUTED=1
      fi

      . prepare_fvm.sh
      pushd "$FVM" || return
      ENABLE_DISTRIBUTED="$ENABLE_DISTRIBUTED" \
        ENABLE_GPU=0 \
        GHEX_BUILD_PREFIX="$PREFIX" \
        INSTALL_PRE_COMMIT=0 \
        MPICC=mpicc \
        MPICXX=mpicxx \
        VENV=venv/"$PREFIX" \
        FRESH_INSTALL=1 \
        INSTALL_PARALLEL_HDF5=1 \
        PARALLEL_HDF5_BUILD_PREFIX="$PREFIX" \
        INSTALL_PARALLEL_NETCDF=1 \
        PARALLEL_NETCDF_BUILD_PREFIX="$PREFIX" \
        . bootstrap_venv.sh

      echo -n "patching netcdf python bindings... "
      pushd _externals/netcdf4-python || return
      mpicc -shared \
        -g -Wl,-rpath,/usr/local/apps/python3/3.8.8-01/lib \
        -L/usr/local/apps/proj/7.2.1/lib -Wl,-rpath,/usr/local/apps/proj/7.2.1/lib \
        -L/usr/local/apps/geos/3.9.1/lib -Wl,-rpath,/usr/local/apps/geos/3.9.1/lib \
        -L/usr/local/apps/openblas/0.3.13/GNU/8.3/lib -Wl,-rpath,/usr/local/apps/openblas/0.3.13/GNU/8.3/lib \
        -g -Wl,-rpath,/usr/local/apps/python3/3."$PYTHON3_MINOR_VERSION"."$PYTHON3_MINOR_VERSION"-01/lib \
        build/temp.linux-x86_64-cpython-3"$PYTHON3_MINOR_VERSION"/src/netCDF4/_netCDF4.o \
        -L"$ROOT"/fvm-gt4py/distributed/_externals/netcdf-c/build/"$PREFIX"/lib \
        -L"$ROOT"/fvm-gt4py/distributed/_externals/hdf5/build/"$PREFIX"/lib \
        -Wl,--enable-new-dtags,-R"$ROOT"/fvm-gt4py/distributed/_externals/netcdf-c/build/"$PREFIX"/lib \
        -Wl,--enable-new-dtags,-R"$ROOT"/fvm-gt4py/distributed/_externals/hdf5/build/"$PREFIX"/lib \
        -lnetcdf -lhdf5_hl -lhdf5 -lm -lz -lsz -lbz2 -lzstd -lxml2 -lcurl -ldl \
        -o build/lib.linux-x86_64-cpython-3"$PYTHON3_MINOR_VERSION"/netCDF4/_netCDF4.cpython-3"$PYTHON3_MINOR_VERSION"-x86_64-linux-gnu.so
      cp build/lib.linux-x86_64-cpython-3"$PYTHON3_MINOR_VERSION"/netCDF4/_netCDF4.cpython-3"$PYTHON3_MINOR_VERSION"-x86_64-linux-gnu.so \
        ../../venv/"$PREFIX"/lib/python3."$PYTHON3_MINOR_VERSION"/site-packages/netCDF4-1.6.3-py3."$PYTHON3_MINOR_VERSION"-linux-x86_64.egg/netCDF4
      echo "OK"

      popd || return
      popd || return
    done
  done
done
