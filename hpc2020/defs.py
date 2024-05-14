# -*- coding: utf-8 -*-
import os
import typing

FloatingPointPrecision = typing.Literal["double", "single"]
MPI = typing.Literal["hpcx", "intelmpi", "openmpi"]
Partition = typing.Literal["gpu", "par"]
ProgrammingEnvironment = typing.Literal["gnu", "intel"]

valid_mpi_libraries = typing.get_args(MPI)
valid_programming_environments = typing.get_args(ProgrammingEnvironment)

root_dir = os.environ.get("HPCPERM", f"/home/{os.getlogin()}")
