# -*- coding: utf-8 -*-
from __future__ import annotations

import common.utils
import common.utils_spack
import defs
import utils_cuda
import utils_mpi


SPACK_PACKAGE_HASHES = {
    "cuda@11.8.0": "hz57wcq",
    "cuda@12.2.0": "2ttufpl",
    "openmpi@4.1.2": "mnmadyt",
    "openmpi@4.1.4": "3ptst2p",
    "openmpi@4.1.5": "godjjas",
    "openmpi@4.1.6": "mjsagqr",
    "openmpi@5.0.5": "wxkyqyp",
    "ucx@1.12.0": "hnlu4xj",
}


def spack_load_mpi(
    compiler: defs.Compiler, mpi: defs.MPI, partition: defs.Partition, num_nodes: int = 1
) -> None:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
            with common.utils.check_argument("partition", partition, defs.valid_partitions):
                assert mpi in defs.compilers_to_mpi_libraries[compiler]

                mpi_ext = None
                if mpi == "hpcx-mpi@2.21":
                    mpi_ext = mpi
                elif mpi == "openmpi@4.1.2":
                    if compiler == "gcc@11.2.0":
                        assert partition != "gpu"
                        mpi_ext = "openmpi@4.1.2 fabrics=knem,ucx"
                elif mpi == "openmpi@4.1.4":
                    if compiler == "gcc@11.2.0":
                        mpi_ext = mpi
                elif mpi == "openmpi@4.1.5":
                    if compiler == "gcc@11.2.0":
                        mpi_ext = "openmpi@4.1.5 +cuda fabrics=knem,ucx"
                elif mpi == "openmpi@4.1.6":
                    if compiler in ["gcc@11.2.0", "nvhpc@23.9"]:
                        mpi_ext = mpi
                elif mpi == "openmpi@5.0.5":
                    if compiler == "gcc@11.2.0":
                        mpi_ext = mpi

                assert mpi_ext is not None
                common.utils_spack.spack_load(mpi_ext, compiler=compiler)
                common.utils.append_to_path(
                    "LD_LIBRARY_PATH", f"$(spack location -i {mpi_ext} %{compiler})/lib"
                )

                if "openmpi" in mpi or "hpcx-mpi" in mpi:
                    common.utils.export_variable("CC", "$(which mpicc)")
                    common.utils.export_variable("CXX", "$(which mpiCC)")
                    common.utils.export_variable("MPICC", "$(which mpicc)")
                    common.utils.export_variable("MPICXX", "$(which mpiCC)")

    utils_mpi.setup_mpi(mpi, partition, num_nodes=num_nodes)


def spack_load_python(python: defs.Python) -> None:
    with common.utils.check_argument("python", python, defs.valid_python_interpreters):
        if python == "python@3.9":
            common.utils_spack.spack_load("python@3.9.9 ~debug", compiler="gcc@11.2.0")
        elif python == "python@3.10":
            common.utils_spack.spack_load("python@3.10.10", compiler="gcc@13.3.0")
        elif python == "python@3.11":
            common.utils_spack.spack_load("python@3.11.9", compiler="gcc@11.2.0")
        elif python == "python@3.12":
            common.utils_spack.spack_load("python@3.12.0", compiler="gcc@11.2.0")


def spack_load_hdf5(compiler: defs.Compiler, mpi: defs.MPI) -> None:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
            assert mpi in defs.compilers_to_mpi_libraries[compiler]
            hdf5 = None
            if compiler in ["gcc@11.2.0", "nvhpc@23.9"]:
                hdf5 = f"hdf5@1.14.3 +mpi"
            assert hdf5 is not None
            common.utils_spack.spack_load(hdf5, compiler=compiler, dependencies=[mpi])
            common.utils.export_variable(
                "HDF5_ROOT", f"$(spack location -i {hdf5} %{compiler} ^{mpi})"
            )
            common.utils.export_variable("HDF5_DIR", "$HDF5_ROOT")


def spack_load_netcdf(compiler: defs.Compiler, mpi: defs.MPI) -> None:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
            assert mpi in defs.compilers_to_mpi_libraries[compiler]
            netcdf = None
            if compiler == "gcc@11.2.0":
                if mpi == "hpcx-mpi@2.21":
                    netcdf = "netcdf-c@main"
                else:
                    netcdf = "netcdf-c@4.9.2 +mpi"
            elif "nvhpc" in compiler:
                netcdf = "netcdf-c@main"
            assert netcdf is not None
            common.utils_spack.spack_load(netcdf, compiler=compiler, dependencies=[mpi])
            common.utils.export_variable(
                "NETCDF_ROOT", f"$(spack location -i {netcdf} %{compiler} ^{mpi})"
            )
            common.utils.export_variable("NETCDF4_DIR", "$NETCDF_ROOT")


def spack_load_cuda(compiler: defs.Compiler, mpi: defs.MPI) -> str:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
            cuda_version = None
            if compiler == "gcc@11.2.0":
                if mpi == "hpcx-mpi@2.21":
                    common.utils.export_variable(
                        "CUDA_HOME",
                        "/sw/spack-levante/nvhpc-24.11-qgwst6/Linux_x86_64/24.11/cuda/12.6/",
                    )
                    common.utils.append_to_path("PATH", "$CUDA_HOME/bin")
                    cuda_version = "12"

                if mpi == "openmpi@4.1.4":
                    common.utils_spack.spack_load("cuda@11.7.0", compiler=compiler)
                    cuda_version = "11"
                elif mpi == "openmpi@4.1.5":
                    common.utils_spack.spack_load("cuda@12.2.0", compiler=compiler)
                    cuda_version = "12"
                elif mpi == "openmpi@4.1.6":
                    # elif mpi in ("openmpi@4.1.6", "hpcx-mpi@2.21"):
                    common.utils_spack.spack_load("cuda@11.8.0/nnw4twu", compiler=compiler)
                    cuda_version = "11"
                elif mpi == "openmpi@5.0.5":
                    common.utils_spack.spack_load("cuda@12.5.1", compiler=compiler)
                    cuda_version = "12"
            elif compiler == "nvhpc@23.9":
                common.utils_spack.spack_load("cuda@11.8", compiler=compiler)
                cuda_version = "11"
            elif compiler == "nvhpc@24.7":
                common.utils.export_variable(
                    "CUDA_HOME",
                    "/sw/spack-levante/nvhpc-24.7-py26uc/Linux_x86_64/24.7/cuda/12.5/",
                )
                common.utils.append_to_path("PATH", "$CUDA_HOME/bin")
                cuda_version = "12"
            assert cuda_version is not None

    utils_cuda.setup_cuda()

    return cuda_version
