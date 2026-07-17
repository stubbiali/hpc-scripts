# -*- coding: utf-8 -*-
import os
from typing import Literal, get_args

user: str = os.environ.get("USER", "subbiali")
fast_dir: str = os.environ.get("FAST", "/leonardo_scratch/fast/DestE_330_26")
user_fast_dir: str = os.path.join(fast_dir, user)

# see https://docs.hpc.cineca.it/hpc/leonardo.html
Partition = Literal["boost_usr_prod"]
QOS: dict[Partition, tuple[str, ...]] = {
    "boost_usr_prod": ("normal", "boost_qos_dbg", "boost_qos_bprod", "boost_qos_lprod")
}
valid_partitions = get_args(Partition)

FloatingPointPrecision = Literal["double", "single"]

Compiler = Literal["gcc", "nvhpc"]
CompilerVersion: dict[Compiler, tuple[str, ...]] = {"gcc": ("12.2.0",), "nvhpc": ("24.5", "25.11")}
valid_compilers = get_args(Compiler)

MPILibrary = Literal["openmpi", "hpcx-mpi"]
MPILIbraryVersion: dict[MPILibrary, tuple[str, ...]] = {
    "openmpi": ("4.1.6", "5.0.9"),
    "hpcx-mpi": ("2.19", "2.25.1"),
}
valid_mpi_libraries = get_args(MPILibrary)

CUDAVersion = Literal["12.2", "12.3", "12.6"]
valid_cuda_versions = get_args(CUDAVersion)

SoftwareStack = Literal["gcc-openmpi", "nvhpc-hpcx-mpi"]
valid_software_stacks = get_args(SoftwareStack)

PythonVersion = Literal["3.11", "3.12", "3.13"]
valid_python_versions = get_args(PythonVersion)
