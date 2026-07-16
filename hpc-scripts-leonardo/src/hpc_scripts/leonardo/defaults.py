# -*- coding: utf-8 -*-

from hpc_scripts.leonardo import defs

ACCOUNT: str = "DestE_330_26"
PARTITION: defs.Partition = "boost_usr_prod"
QOS: dict[defs.Partition, str] = {"boost_usr_prod": "normal", "lrd_all_serial": "normal"}

COMPILER: defs.Compiler = "gcc"
COMPILER_VERSIONS: dict[defs.Compiler, str] = {"gcc": "12.2.0", "nvhpc": "25.11"}

CUDA_VERSION: defs.CUDAVersion = "12.2"

MPI_LIBRARY: defs.MPILibrary = "openmpi"
MPI_LIBRARY_VERSIONS: dict[defs.MPILibrary, str] = {"openmpi": "4.1.6", "hpcx-mpi": "2.25.1"}

SOFTWARE_STACK: defs.SoftwareStack = "gcc-openmpi"
PYTHON_VERSION: defs.PythonVersion = "3.11"
