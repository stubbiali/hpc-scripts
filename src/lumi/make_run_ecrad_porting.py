#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import Literal, TYPE_CHECKING

import common.utils
import common.utils_module
import defaults
import make_prepare_ecrad_porting
import utils

if TYPE_CHECKING:
    import defs


# >>> config: start
BRANCH: str = "solvers-cy49r1"
DACE_DEFAULT_BLOCK_SIZE: str = ""
ECRAD_ENABLE_CHECKS: bool = True
ECRAD_MODE: Literal["fortran", "gt4py"] = "gt4py"
ECRAD_NUM_RUNS: int = 0
ECRAD_PRECISION: defs.FloatingPointPrecision = "double"
ECRAD_STENCIL_NAME: str = "ecrad_ecckd_tripleclouds"
ECRAD_STENCIL_VERSION: str = "cy49r1s"
ECRAD_VERBOSE: bool = True
GT_BACKEND: str = "gt:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
# >>> config: end


def core(
    branch: str,
    dace_default_block_size: str,
    ecrad_enable_checks: bool,
    ecrad_mode: Literal["fortran", "gt4py"],
    ecrad_num_runs: int,
    ecrad_precision: defs.FloatingPointPrecision,
    ecrad_stencil_name: str,
    ecrad_stencil_version: str,
    ecrad_verbose: bool,
    env: defs.ProgrammingEnvironment,
    gt_backend: str,
    hdf5_version: str,
    netcdf_version: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    partition: defs.Partition,
    rocm_version: str,
    stack: defs.SoftwareStack,
    stack_version: str,
) -> str:
    prepare_ecrad_fname = make_prepare_ecrad_porting.core(
        branch,
        env,
        hdf5_version,
        netcdf_version,
        partition,
        rocm_version,
        stack,
        stack_version,
    )

    with common.utils.batch_file(filename="run_ecrad_porting") as (_, fname):
        common.utils.run(f"source {prepare_ecrad_fname}")

        with common.utils.chdir("$ECRAD"):
            common.utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
            common.utils.export_variable("OMP_PLACES", "cores")
            common.utils.export_variable("OMP_PROC_BIND", "close")
            # common.utils.export_variable("OMP_DISPLAY_AFFINITY", "True")
            common.utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=32768'")
            if utils.get_partition_type(partition) == "gpu":
                common.utils.export_variable("DACE_DEFAULT_BLOCK_SIZE", dace_default_block_size)

            srun_options = utils.get_srun_options(
                num_nodes,
                num_tasks_per_node,
                num_threads_per_task,
                partition,
                gt_backend=gt_backend,
            )
            ecrad_command = f"ecrad_{ecrad_mode} --name={ecrad_stencil_name} --version={ecrad_stencil_version} --precision={ecrad_precision} --num-runs={ecrad_num_runs} {'--verbose ' if ecrad_verbose else ''}"
            if ecrad_mode == "gt4py":
                ecrad_command += (
                    f"--backend={gt_backend} {'--enable-checks' if ecrad_enable_checks else ''}"
                )
            command = (
                f"CC=cc CXX=CC srun {' '.join(srun_options)} ./../../select_gpu.sh {ecrad_command}"
            )

            for _ in range(num_runs):
                common.utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--dace-default-block-size", type=str, default=DACE_DEFAULT_BLOCK_SIZE)
    parser.add_argument("--ecrad-enable-checks", type=bool, default=ECRAD_ENABLE_CHECKS)
    parser.add_argument("--ecrad-mode", type=str, default=ECRAD_MODE)
    parser.add_argument("--ecrad-num-runs", type=int, default=ECRAD_NUM_RUNS)
    parser.add_argument("--ecrad-precision", type=str, default=ECRAD_PRECISION)
    parser.add_argument("--ecrad-stencil-name", type=str, default=ECRAD_STENCIL_NAME)
    parser.add_argument("--ecrad-stencil-version", type=str, default=ECRAD_STENCIL_VERSION)
    parser.add_argument("--ecrad-verbose", type=bool, default=ECRAD_VERBOSE)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=defaults.NETCDF_VERSION)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--rocm-version", type=str, default=defaults.ROCM_VERSION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    args = parser.parse_args()
    with common.utils.batch_directory():
        core(**args.__dict__)
