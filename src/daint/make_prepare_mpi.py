#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import TYPE_CHECKING

import common.utils
import defaults

if TYPE_CHECKING:
    import defs


def core(partition: defs.Partition) -> str:
    with common.utils.batch_file(filename="prepare_mpi") as (f, fname):
        # configure MPICH
        common.utils.export_variable("MPICH_CRAY_OPT_THREAD_SYNC", 1)
        common.utils.export_variable("MPICH_GNI_USE_UNASSIGNED_CPUS", "enabled")
        common.utils.export_variable("MPICH_MAX_THREAD_SAFETY", "multiple")
        common.utils.export_variable("MPICH_NEMESIS_ASYNC_PROGRESS", "MC")
        common.utils.export_variable("MPICH_NEMESIS_ON_NODE_ASYNC_OPT", 1)
        common.utils.export_variable("MPICH_OPTIMIZED_MEMCPY", 2)
        if partition == "gpu":
            common.utils.export_variable("MPICH_GPU_SUPPORT_ENABLED", 1)
            common.utils.export_variable("CRAY_ACCEL_TARGET", "nvidia60")
            common.utils.export_variable("MPICH_RDMA_ENABLED_CUDA", 1)
        else:
            common.utils.export_variable("MPICH_GPU_SUPPORT_ENABLED", 0)
    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure MPICH.")
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
