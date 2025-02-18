#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import TYPE_CHECKING

import common.utils
import common.utils_module
import common.utils_spack
import utils_module

if TYPE_CHECKING:
    import defs


# >>> config: start
COMPILER: defs.Compiler = "gcc@11.2.0"
MPI: defs.MPI = "openmpi@4.1.6"
PARTITION: defs.Partition = "gpu"
# >>> config: end


def core(compiler: defs.Compiler, mpi: defs.MPI, partition: defs.Partition):
    with common.utils.batch_file(prefix="spack_install"):
        common.utils_module.module_purge(force=True)
        common.utils_spack.spack_unload()

        utils_module.module_load_compiler(compiler)
        # utils_spack.spack_load_mpi(compiler, mpi, partition)

        common.utils_spack.spack_install("libiconv@1.17", compiler=compiler)
        common.utils_spack.spack_install("neovim@0.10.0", compiler=compiler)
        # common.utils_spack.spack_install("python@3.12.0 +optimizations", compiler=compiler)
        common.utils_spack.spack_install("boost@1.85.0", compiler=compiler)
        common.utils_spack.spack_install(
            "openmpi@4.1.6 "
            "+cuda ~internal-hwloc ~internal-pmix +rsh +static +vt +wrapper-rpath "
            "cuda_arch=80 fabrics=knem,ucx romio-filesystem=lustre,nfs,testfs schedulers=slurm",
            compiler=compiler,
            dependencies=["cuda@11.8.0", "knem@1.1.4.90mlnx2", "slurm@23.02.7", "ucx@1.12.0"],
        )
        common.utils_spack.spack_install(
            "hdf5@1.14.3 +cxx +fortran +hl +mpi +shared +threadsafe +tools",
            compiler=compiler,
            dependencies=[mpi],
        )
        common.utils_spack.spack_install(
            "netcdf-c@4.9.2 +mpi +hdf4 +parallel-netcdf", compiler=compiler, dependencies=[mpi]
        )

        # common.utils_spack.spack_install(
        #     "ucx@1.12.0 "
        #     "+cma +cuda +dm +examples +gdrcopy +knem +mlx5_dv +openmp +optimizations "
        #     "+pic +rc +rdmacm +thread_multiple +verbs "
        #     "cuda_arch=80 libs=shared,static opt=3 simd=auto",
        #     compiler=compiler,
        # )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", type=str, default=COMPILER)
    parser.add_argument("--mpi", type=str, default=MPI)
    parser.add_argument("--partition", type=str, default=PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
