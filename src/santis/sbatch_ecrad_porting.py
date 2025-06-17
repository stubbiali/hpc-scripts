#!/users/subbiali/spack/c4449cb201/opt/spack/linux-sles15-neoverse_v2/gcc-13.3.0/python-3.12.9-t554gwycoz72hebgyyp6am6btc6pfa4m/bin/python3.12
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools
from typing import Literal

import common.utils
import defs
import make_run_ecrad_porting
import sbatch


# >>> config: start
ACCOUNT: defs.Account = "c46"
BRANCH: str = "solvers-cy49r1-dev"
DACE_DEFAULT_BLOCK_SIZE: str = "1024,1,1"
DRY_RUN: bool = False
ECRAD_ENABLE_CHECKS: bool = True
ECRAD_MODE: Literal["fortran", "gt4py"] = "gt4py"
ECRAD_NUM_RUNS: int = 0
ECRAD_PRECISION: list[defs.FloatingPointPrecision] = ["double"]
ECRAD_STENCIL_NAME: list[str] = ["solver_tripleclouds_lw"]
ECRAD_STENCIL_VERSION: list[str] = ["cy49r1s"]
ECRAD_VERBOSE: bool = True
GT_BACKEND: list[str] = ["gt:gpu"]
NUM_RUNS: int = 1
PARTITION: defs.Partition = "normal"
PYTHON_VERSION: defs.PythonVersion = "3.11"
TIME: str = "24:00:00"
# >>> config: end


def core():
    for ecrad_precision, ecrad_stencil_name, ecrad_stencil_version, gt_backend in itertools.product(
        ECRAD_PRECISION, ECRAD_STENCIL_NAME, ECRAD_STENCIL_VERSION, GT_BACKEND
    ):
        job_dir = (
            f"ecrad-porting/{BRANCH}/_jobs/{PARTITION}/{ECRAD_MODE}/{ecrad_stencil_version}/"
            f"{ecrad_stencil_name}/"
        )
        job_dir += (
            f"{ecrad_precision}"
            if ECRAD_MODE == "fortran"
            else f"{gt_backend.replace(':', '')}/{ecrad_precision}"
        )
        with common.utils.batch_directory(path=job_dir):
            job_name = (
                f"ecrad_{ECRAD_MODE}-{ecrad_stencil_name}-{ecrad_stencil_version}-"
                f"{gt_backend}-{ecrad_precision[0]}"
            )
            job_script = make_run_ecrad_porting.core(
                branch=BRANCH,
                dace_default_block_size=DACE_DEFAULT_BLOCK_SIZE,
                ecrad_enable_checks=ECRAD_ENABLE_CHECKS,
                ecrad_mode=ECRAD_MODE,
                ecrad_num_runs=ECRAD_NUM_RUNS,
                ecrad_precision=ecrad_precision,
                ecrad_stencil_name=ecrad_stencil_name,
                ecrad_stencil_version=ecrad_stencil_version,
                ecrad_verbose=ECRAD_VERBOSE,
                gt_backend=gt_backend,
                num_nodes=(num_nodes := 1),
                num_runs=NUM_RUNS,
                num_tasks_per_node=(num_tasks_per_node := 1),
                num_threads_per_task=64,
                python_version=PYTHON_VERSION,
            )
            sbatch.core(
                account=ACCOUNT,
                dry_run=DRY_RUN,
                job_name=job_name,
                job_script=job_script,
                num_nodes=num_nodes,
                num_tasks_per_node=num_tasks_per_node,
                partition=PARTITION,
                time=TIME,
            )


if __name__ == "__main__":
    core()
