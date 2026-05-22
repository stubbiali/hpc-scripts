#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
from __future__ import annotations

import itertools
import os
from typing import Literal

from hpc_scripts import common
from hpc_scripts.santis import defaults, defs, make_run_ecrad_versions, sbatch, utils

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
UENV: defs.UEnv = defaults.UENV
# >>> config: end


def main():
    for ecrad_precision, ecrad_stencil_name, ecrad_stencil_version, gt_backend in itertools.product(
        ECRAD_PRECISION, ECRAD_STENCIL_NAME, ECRAD_STENCIL_VERSION, GT_BACKEND
    ):
        job_dir = os.path.join(
            defs.jobs_root_dir,
            utils.get_uenv_with_dashes(UENV),
            "ecrad-versions",
            BRANCH,
            ECRAD_MODE,
            ecrad_stencil_version,
            ecrad_stencil_name,
            ecrad_precision
            if ECRAD_MODE == "fortran"
            else f"{gt_backend.replace(':', '')}/{ecrad_precision}",
        )
        with common.utils.output_directory(path=job_dir):
            job_name = (
                f"ecrad_{ECRAD_MODE}-{ecrad_stencil_name}-{ecrad_stencil_version}-"
                f"{gt_backend}-{ecrad_precision[0]}"
            )
            job_script = make_run_ecrad_versions.core(
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
    main()
