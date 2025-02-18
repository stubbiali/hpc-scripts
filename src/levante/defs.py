# -*- coding: utf-8 -*-
from typing import Literal, get_args

Compiler = Literal["gcc@11.2.0", "gcc@13.3.0", "nvhpc@23.9", "nvhpc@24.7"]
FloatingPointPrecision = Literal["double", "single"]
MPI = Literal[
    "hpcx-mpi@2.21",
    "openmpi@4.1.2",
    "openmpi@4.1.4",
    "openmpi@4.1.5",
    "openmpi@4.1.6",
    "openmpi@5.0.5",
]
Partition = Literal["compute", "gpu"]
Python = Literal["python@3.9", "python@3.10", "python@3.11", "python@3.12"]

valid_compilers = get_args(Compiler)
valid_mpi = get_args(MPI)
valid_partitions = get_args(Partition)
valid_python_interpreters = get_args(Python)

compilers_to_mpi_libraries: dict[Compiler, list[MPI]] = {
    "gcc@11.2.0": [
        "hpcx-mpi@2.21",
        "openmpi@4.1.2",
        "openmpi@4.1.4",
        "openmpi@4.1.5",
        "openmpi@4.1.6",
        "openmpi@5.0.5",
    ],
    "gcc@13.3.0": [],
    "nvhpc@23.9": ["openmpi@4.1.6"],
    "nvhpc@24.7": ["openmpi@4.1.5"],
}
