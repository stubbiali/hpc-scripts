# -*- coding: utf-8 -*-
from __future__ import annotations

import common.utils
import common.utils_module
import defs


def load_partition(partition: defs.Partition) -> None:
    with common.utils.check_argument("partition", partition, defs.valid_partitions):
        common.utils_module.module_load(f"daint-{partition}")


def load_env(env: defs.ProgrammingEnvironment) -> None:
    with common.utils.check_argument("env", env, defs.valid_programming_environments):
        common.utils_module.module_load("PrgEnv-gnu")


def setup_env(env: defs.ProgrammingEnvironment, partition: defs.Partition) -> None:
    with common.utils.check_argument("env", env, defs.valid_programming_environments):
        with common.utils.check_argument("partition", partition, defs.valid_partitions):
            common.utils_module.module_purge(force=True)
            load_partition(partition)
            load_env(env)


def setup_cuda() -> None:
    common.utils.run("NVCC_PATH=$(which nvcc)")
    common.utils.run("CUDA_PATH=$(echo $NVCC_PATH | sed -e 's/\/bin\/nvcc//g')")
    common.utils.export_variable("CUDA_HOME", "$CUDA_PATH")
    common.utils.export_variable("LD_LIBRARY_PATH", "$CUDA_PATH/lib64:$LD_LIBRARY_PATH")
    common.utils.export_variable("CRAY_CUDA_MPS", "1")
