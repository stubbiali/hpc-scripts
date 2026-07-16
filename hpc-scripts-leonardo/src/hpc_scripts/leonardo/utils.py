# -*- coding: utf-8 -*-
from __future__ import annotations

import contextlib
import dataclasses
import os
from typing import TYPE_CHECKING

from hpc_scripts import common
from hpc_scripts.leonardo import defaults, defs

if TYPE_CHECKING:
    from typing import Optional


@dataclasses.dataclass(frozen=True)
class PartitionInfo:
    max_num_nodes: int
    max_walltime: str
    min_num_nodes: int = 1


def _get_partition_info(partition: defs.Partition, qos: defs.QOS) -> PartitionInfo:
    with common.utils.check_argument("partition", partition, defs.valid_partitions):
        with common.utils.check_argument("qos", qos, defs.QOS[partition]):
            return {
                "normal": PartitionInfo(max_num_nodes=64, max_walltime="24:00:00"),
                "boost_qos_dbg": PartitionInfo(max_num_nodes=8, max_walltime="00:30:00"),
                "boost_qos_bprod": PartitionInfo(
                    min_num_nodes=65, max_num_nodes=256, max_walltime="24:00:00"
                ),
                "boost_qos_lprod": PartitionInfo(max_num_nodes=8, max_walltime="4-00:00:00"),
            }[qos]


def check_slurm_settings(
    partition: defs.Partition, qos: defs.QOS, num_nodes: int, time: Optional[str]
) -> str:
    pinfo = _get_partition_info(partition, qos)

    if not pinfo.min_num_nodes <= num_nodes <= pinfo.max_num_nodes:
        raise RuntimeError(
            f"{num_nodes=} is not in the allowed range "
            f"[{pinfo.min_num_nodes}, {pinfo.max_num_nodes}]."
        )

    time = time or pinfo.max_walltime
    if time > pinfo.max_walltime:
        raise RuntimeError(f"{time=} is larger than the maximum wall-time {pinfo.max_walltime}.")

    return time


@contextlib.contextmanager
def check_args(
    compiler: defs.Compiler,
    compiler_version: str,
    mpi: defs.MPILibrary,
    mpi_version: str,
    cuda_version: Optional[defs.CUDAVersion] = None,
):
    try:
        with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
            with common.utils.check_argument(
                "compiler_version", compiler_version, defs.CompilerVersion[compiler]
            ):
                ...
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi_libraries):
            with common.utils.check_argument(
                "mpi_version", mpi_version, defs.MPILIbraryVersion[mpi]
            ):
                ...
        if cuda_version is not None:
            with common.utils.check_argument(
                "cuda_version", cuda_version, defs.valid_cuda_versions
            ):
                ...
        yield None
    finally:
        ...


def get_compiler_and_mpi_and_cuda(
    software_stack: defs.SoftwareStack,
) -> tuple[defs.Compiler, str, defs.MPILibrary, str, defs.CUDAVersion]:
    with common.utils.check_argument("software_stack", software_stack, defs.valid_software_stacks):
        if software_stack == "gcc-openmpi":
            compiler, mpi = "gcc", "openmpi"
        else:  # software_stack == "nvhpc-hpcx-mpi":
            compiler, mpi = "nvhpc", "hpcx-mpi"

        return (
            compiler,
            defaults.COMPILER_VERSIONS[compiler],
            mpi,
            defaults.MPI_LIBRARY_VERSIONS[mpi],
            defaults.CUDA_VERSION,
        )


def load_mpi(
    compiler: defs.Compiler,
    compiler_version: str,
    mpi: defs.MPILibrary,
    mpi_version: str,
    cuda_version: defs.CUDAVersion,
) -> None:
    with check_args(compiler, compiler_version, mpi, mpi_version, cuda_version):
        common.utils_module.module_load(f"{compiler}/{compiler_version}")
        if mpi == "openmpi":
            common.utils_module.module_load(
                f"{mpi}/{mpi_version}--{compiler}--{compiler_version}-cuda-{cuda_version}"
            )
        elif mpi == "hpcx-mpi":
            common.utils_module.module_load(f"{mpi}/{mpi_version}")
            common.utils.export_variable("CFLAGS", "'$CFLAGS -noswitcherror'")

        common.utils.export_variable("CC", "$(which mpicc)")
        common.utils.export_variable("CXX", "$(which mpic++)")
        common.utils.export_variable("MPICC", "$(which mpicc)")
        common.utils.export_variable("MPICXX", "$(which mpic++)")


def load_boost(
    compiler: defs.Compiler, compiler_version: str, mpi: defs.MPILibrary, mpi_version: str
) -> None:
    with check_args(compiler, compiler_version, mpi, mpi_version):
        if (compiler, compiler_version, mpi, mpi_version) == (
            "nvhpc",
            "25.11",
            "hpcx-mpi",
            "2.25.1",
        ):
            common.utils_module.module_load("boost/1.85.0--gcc--12.2.0")
        else:
            common.utils_module.module_load(
                f"boost/1.85.0--{mpi}--{mpi_version}--{compiler}--{compiler_version}"
            )


def load_cuda(cuda_version: defs.CUDAVersion) -> None:
    with common.utils.check_argument("cuda_version", cuda_version, defs.valid_cuda_versions):
        common.utils_module.module_load(f"cuda/{cuda_version}")


def load_hdf5(
    compiler: defs.Compiler, compiler_version: str, mpi: defs.MPILibrary, mpi_version: str
) -> None:
    with check_args(compiler, compiler_version, mpi, mpi_version):
        module_name = f"hdf5/1.14.3--{mpi}--{mpi_version}--{compiler}--{compiler_version}"
        if compiler == "gcc" and mpi == "openmpi":
            module_name += "-spack0.22"
        common.utils_module.module_load(module_name)


def load_netcdf(
    compiler: defs.Compiler, compiler_version: str, mpi: defs.MPILibrary, mpi_version: str
) -> None:
    with check_args(compiler, compiler_version, mpi, mpi_version):
        module_name = f"netcdf-c/4.9.2--{mpi}--{mpi_version}--{compiler}--{compiler_version}"
        if compiler == "gcc" and mpi == "openmpi":
            module_name += "-spack0.22"
        common.utils_module.module_load(module_name)


def load_python(python_version: defs.PythonVersion) -> None:
    with common.utils.check_argument("python_version", python_version, defs.valid_python_versions):
        if python_version == "3.11":
            common.utils_module.module_load("python")


def load_pmap_stack(python_version: defs.PythonVersion, software_stack: defs.SoftwareStack) -> None:
    compiler, compiler_version, mpi, mpi_version, cuda_version = get_compiler_and_mpi_and_cuda(
        software_stack
    )
    load_mpi(compiler, compiler_version, mpi, mpi_version, cuda_version)
    load_cuda(cuda_version)
    load_boost(compiler, compiler_version, mpi, mpi_version)
    load_hdf5(compiler, compiler_version, mpi, mpi_version)
    load_netcdf(compiler, compiler_version, mpi, mpi_version)
    load_python(python_version)


def setup_uv(software_stack: defs.SoftwareStack) -> None:
    common.utils.export_variable(
        "UV_CACHE_DIR", os.path.join(defs.user_fast_dir, "_uvcache", software_stack)
    )


def setup_ghex() -> None:
    common.utils.export_variable("GHEX_TRANSPORT_BACKEND", "MPI")
    common.utils.export_variable("GHEX_USE_GPU", 1)
    common.utils.export_variable("GHEX_GPU_TYPE", "NVIDIA")
    common.utils.export_variable("GHEX_GPU_ARCH", "80")
