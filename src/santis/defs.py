# -*- coding: utf-8 -*-
import os
import typing

Account = typing.Literal["c28", "c46"]
Partition = typing.Literal["debug", "normal"]
scratch_dir: str = os.environ.get("SCRATCH", "/capstor/scratch/cscs/subbiali")

spack_pmap_root: str = "/capstor/scratch/cscs/ciextc28/software_stack/spack"
spack_pmap_env: str = "python_cuda_alps-santis"

PythonVersion = typing.Literal["3.10", "3.11", "3.12"]
valid_python_versions = typing.get_args(PythonVersion)

FloatingPointPrecision = typing.Literal["double", "single"]
