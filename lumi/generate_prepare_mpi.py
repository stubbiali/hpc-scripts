#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import defs
import utils


# >>> config: start
PARTITION_TYPE: defs.PartitionType = "gpu"
# >>> config: end


def core(partition_type: defs.PartitionType) -> str:
    with utils.batch_file(prefix="prepare_mpi") as (f, fname):
        # configure MPICH
        # utils.export_variable("MPICH_CRAY_OPT_THREAD_SYNC", 1)
        # utils.export_variable("MPICH_GNI_USE_UNASSIGNED_CPUS", "enabled")
        # utils.export_variable("MPICH_NEMESIS_ASYNC_PROGRESS", "MC")
        # utils.export_variable("MPICH_NEMESIS_ON_NODE_ASYNC_OPT", 1)
        # utils.export_variable("MPICH_OPTIMIZED_MEMCPY", 2)
        utils.export_variable("MPICH_MAX_THREAD_SAFETY", "multiple")
        if partition_type == "gpu":
            utils.export_variable("MPICH_GPU_SUPPORT_ENABLED", 1)
            utils.export_variable("MPICH_RDNA_ENABLED_CUDA", 1)
        else:
            utils.export_variable("MPICH_GPU_SUPPORT_ENABLED", 0)
    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure MPICH.")
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    args = parser.parse_args()
    core(**args.__dict__)
