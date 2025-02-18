#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import update_path  # noqa: F401

import common.utils as common_utils
import defs


# >>> config: start
PARTITION: defs.Partition = "gpu"
# >>> config: end


def core(partition: defs.Partition) -> str:
    with common_utils.batch_file(filename="prepare_mpi") as (f, fname):
        # configure MPICH
        common_utils.export_variable("MPICH_CRAY_OPT_THREAD_SYNC", 1)
        common_utils.export_variable("MPICH_GNI_USE_UNASSIGNED_CPUS", "enabled")
        common_utils.export_variable("MPICH_MAX_THREAD_SAFETY", "multiple")
        common_utils.export_variable("MPICH_NEMESIS_ASYNC_PROGRESS", "MC")
        common_utils.export_variable("MPICH_NEMESIS_ON_NODE_ASYNC_OPT", 1)
        common_utils.export_variable("MPICH_OPTIMIZED_MEMCPY", 2)
        if partition == "gpu":
            common_utils.export_variable("MPICH_GPU_SUPPORT_ENABLED", 1)
            common_utils.export_variable("CRAY_ACCEL_TARGET", "nvidia60")
            common_utils.export_variable("MPICH_RDMA_ENABLED_CUDA", 1)
        else:
            common_utils.export_variable("MPICH_GPU_SUPPORT_ENABLED", 0)
    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure MPICH.")
    parser.add_argument("--partition", type=str, default=PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
