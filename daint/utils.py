# -*- coding: utf-8 -*-
from __future__ import annotations

import update_path  # noqa: F401

import common_utils
import defs


def load_partition(partition: defs.Partition) -> None:
    with check_argument("partition", partition, defs.valid_partitions):
        common_utils.module_load(f"daint-{partition}")


def load_env(env: defs.ProgrammingEnvironment) -> None:
    with check_argument("env", env, defs.valid_programming_environments):
        common_utils.module_load("PrgEnv-gnu")


def setup_env(env: defs.ProgrammingEnvironment, partition: defs.Partition) -> None:
    with check_argument("env", env, defs.valid_programming_environments):
        with check_argument("partition", partition, defs.valid_partitions):
            common_utils.module_purge(force=True)
            load_partition(partition)
            load_env(env)


def setup_cuda():
    common_utils.run("NVCC_PATH=$(which nvcc)")
    common_utils.run("CUDA_PATH=$(echo $NVCC_PATH | sed -e 's/\/bin\/nvcc//g')")
    common_utils.export_variable("CUDA_HOME", "$CUDA_PATH")
    common_utils.export_variable("LD_LIBRARY_PATH", "$CUDA_PATH/lib64:$LD_LIBRARY_PATH")
    common_utils.export_variable("CRAY_CUDA_MPS", "1")
