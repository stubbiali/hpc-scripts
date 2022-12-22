#!/bin/bash -l

BRANCH=distributed-dev
ENV_L=( amd )
MPI_L=( openmpi intel hpcx )

mkdir -p fvm-gt4py/"$BRANCH"/venv

for ENV in "${ENV_L[@]}"; do
  for MPI in "${MPI_L[@]}"; do
    . prepare_fvm.sh
    pushd "$FVM" || return
    ENABLE_DISTRIBUTED=0 VENV=venv/"$ENV"-"$MPI" INSTALL_PRE_COMMIT=0 . bootstrap_venv.sh
    . venv/"$ENV"-"$MPI"/bin/activate
    MPICC=mpicc pip install mpi4py --no-cache
    pushd externals/ghex-py-bindings-debug || return
    mkdir -p build/"$ENV"-"$MPI"/cpu
    pushd build/"$ENV"-"$MPI"/cpu || return
    CXX=mpicxx \
        cmake ../../.. \
        -DCMAKE_BUILD_TYPE=Release \
        -DGHEX_BUILD_PYTHON_BINDINGS=On \
        -DPY_MPI4PY="$FVM"/venv/"$ENV"-"$MPI"/lib/python3.8/site-packages/mpi4py \
        -DHAVE_MPI4PY=True
    make
    # GHEX_PY_LIB_PATH=$PWD
    popd || return
    pushd bindings/python || return
    pip install -e .
    popd || return
    popd || return
    # echo -e "\nexport GHEX_PY_LIB_PATH=$GHEX_PY_LIB_PATH" >> venv/"$ENV"/"$MPI"/bin/activate
    # echo -e "\nexport GT_CACHE_ROOT=$PWD/gt_cache/$ENV" >> venv/"$ENV"/"$MPI"/bin/activate
    popd || return
    deactivate
  done
done
