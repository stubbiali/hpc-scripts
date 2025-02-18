# -*- coding: utf-8 -*-
from __future__ import annotations

import common.utils
import defs
import utils_module
import utils_spack


def load_mpi(
    compiler: defs.Compiler, mpi: defs.MPI, partition: defs.Partition, num_nodes: int = 1
) -> None:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
            if "nvhpc" in compiler and "openmpi" in mpi:
                utils_module.module_load_mpi(compiler, mpi)
            else:
                utils_spack.spack_load_mpi(compiler, mpi, partition, num_nodes)


def setup_mpi(mpi: defs.MPI, partition: defs.Partition, num_nodes: int = 1) -> None:
    with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
        with common.utils.check_argument("partition", partition, defs.valid_partitions):
            if "openmpi" in mpi:
                # from https://docs.dkrz.de/doc/levante/running-jobs/runtime-settings.html#openmpi
                common.utils.export_variable("OMPI_MCA_osc", "ucx")
                common.utils.export_variable("OMPI_MCA_pml", "ucx")
                common.utils.export_variable("OMPI_MCA_btl", "self")
                common.utils.export_variable("UCX_HANDLE_ERRORS", "bt")
                common.utils.export_variable("OMPI_MCA_pml_ucx_opal_mem_hooks", 1)
                common.utils.export_variable("OMPI_MCA_io", "romio321")
                if num_nodes < 150:
                    common.utils.export_variable("UCX_TLS", "shm,rc_mlx5,rc_x,self")
                else:
                    common.utils.export_variable("UCX_TLS", "shm,dc_mlx5,dc_x,self")
                if partition != "gpu":
                    common.utils.export_variable("UCX_UNIFIED_MODE", "y")
                common.utils.export_variable("OMPI_MCA_coll_tuned_use_dynamic_rules", "true")
                common.utils.export_variable("OMPI_MCA_coll_tuned_alltoallv_algorithm", 2)
