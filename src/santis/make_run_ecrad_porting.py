#!/users/subbiali/spack/c4449cb201/opt/spack/linux-sles15-neoverse_v2/gcc-13.3.0/python-3.12.9-t554gwycoz72hebgyyp6am6btc6pfa4m/bin/python3.12
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import Literal

import common.utils
import defs
import make_prepare_ecrad_porting


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
NUM_THREADS_PER_TASK: int = 64
PYTHON_VERSION: defs.PythonVersion = "3.11"
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
    gt_backend: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    python_version: defs.PythonVersion,
) -> str:
    prepare_ecrad_fname = make_prepare_ecrad_porting.core(branch, python_version)

    with common.utils.batch_file(filename="run_ecrad_porting") as (_, fname):
        common.utils.run(f"source {prepare_ecrad_fname}")

        with common.utils.chdir("$ECRAD"):
            common.utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
            common.utils.export_variable("OMP_PLACES", "cores")
            common.utils.export_variable("OMP_PROC_BIND", "close")
            # common.utils.export_variable("OMP_DISPLAY_AFFINITY", "True")
            # common.utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=32768'")
            common.utils.export_variable("DACE_DEFAULT_BLOCK_SIZE", dace_default_block_size)
            if gt_backend in ["cuda", "dace:gpu", "gt:gpu"]:
                common.utils.export_variable("CUDA_HOST_CXX", "$CXX")

            srun_options = (
                f"--nodes={num_nodes} --ntasks-per-node={num_tasks_per_node} --gpus-per-task=1"
            )
            ecrad_command = (
                f"ecrad_{ecrad_mode} --name={ecrad_stencil_name} "
                f"--version={ecrad_stencil_version} --precision={ecrad_precision} "
                f"--num-runs={ecrad_num_runs} {'--verbose ' if ecrad_verbose else ''}"
            )
            if ecrad_mode == "gt4py":
                ecrad_command += (
                    f"--backend={gt_backend} {'--enable-checks' if ecrad_enable_checks else ''}"
                )
            command = f"srun {srun_options} time {ecrad_command}"

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
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--python-version", type=str, default=defs.PythonVersion)
    args = parser.parse_args()
    with common.utils.batch_directory():
        core(**args.__dict__)
