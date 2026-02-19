# -*- coding: utf-8 -*-
import os
import typing

Account = typing.Literal["c28", "c46"]
Partition = typing.Literal["debug", "normal"]

home_dir: str = os.environ.get("HOME", "/users/subbiali")
project_dir: str = os.environ.get("PROJECT", "/capstor/store/cscs/pasc/c46/subbiali")
scratch_dir: str = os.environ.get("SCRATCH", "/capstor/scratch/cscs/subbiali")

spack_root: str = "/users/subbiali/spack/08eaa297ea"
spack_pmap_root: str = "/capstor/scratch/cscs/ciextc28/software_stack/spack"
spack_pmap_env: str = "python_cuda_alps-santis"

PythonVersion = typing.Literal["3.10", "3.11", "3.12", "3.13", "3.14"]
valid_python_versions = typing.get_args(PythonVersion)

FloatingPointPrecision = typing.Literal["double", "single"]

GHEXTransportBackend = typing.Literal["mpi", "libfabric"]
valid_ghex_transport_backends = typing.get_args(GHEXTransportBackend)

UEnv = typing.Literal["prgenv-gnu/24.11:v2", "prgenv-gnu/25.6:v2"]
valid_uenvs = typing.get_args(UEnv)

uenv_spack_builds_root: str = os.path.join(project_dir, "subbiali/uenv-spack-builds")
