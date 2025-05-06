#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools
from typing import Literal, TYPE_CHECKING

import common.utils
import defaults
import make_run_ecrad_porting
import sbatch

if TYPE_CHECKING:
    import defs


# >>> config: start
ACCOUNT: int = defaults.ACCOUNT
BRANCH: str = "solvers-cy49r1"
DACE_DEFAULT_BLOCK_SIZE: str = "'256,1,1'"
DRY_RUN: bool = False
ECRAD_ENABLE_CHECKS: bool = True
ECRAD_MODE: Literal["fortran", "gt4py"] = "gt4py"
ECRAD_NUM_RUNS: int = 2
ECRAD_PRECISION: list[defs.FloatingPointPrecision] = ["double"]
ECRAD_STENCIL_NAME: list[str] = ["ecrad_ecckd_tripleclouds"]
ECRAD_STENCIL_VERSION: list[str] = ["cy49r1s"]
ECRAD_VERBOSE: bool = True
ENV: defs.ProgrammingEnvironment = "cray"
GT_BACKEND: list[str] = ["dace:gpu"]
HDF5_VERSION: str = defaults.HDF5_VERSION
NETCDF_VERSION: str = defaults.NETCDF_VERSION
NUM_RUNS: int = 3
PARTITION: defs.Partition = "standard-g"
ROCM_VERSION: str = defaults.ROCM_VERSION
STACK: defs.SoftwareStack = defaults.STACK
STACK_VERSION: str = defaults.STACK_VERSION
TIME: str = "02:00:00"
# >>> config: end


def core():
    for ecrad_precision, ecrad_stencil_name, ecrad_stencil_version, gt_backend in itertools.product(
        ECRAD_PRECISION, ECRAD_STENCIL_NAME, ECRAD_STENCIL_VERSION, GT_BACKEND
    ):
        job_dir = f"ecrad-porting/{BRANCH}/_jobs/{PARTITION}/{ECRAD_MODE}/{ecrad_stencil_version}/{ecrad_stencil_name}/"
        job_dir += (
            f"{ecrad_precision}"
            if ECRAD_MODE == "fortran"
            else f"{gt_backend.replace(':', '')}/{ecrad_precision}"
        )
        with common.utils.batch_directory(path=job_dir):
            job_name = f"ecrad_{ECRAD_MODE}-{ecrad_stencil_name}-{ecrad_stencil_version}-{gt_backend}-{ecrad_precision[0]}"
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
                env=ENV,
                gt_backend=gt_backend,
                hdf5_version=HDF5_VERSION,
                netcdf_version=NETCDF_VERSION,
                num_nodes=(num_nodes := 1),
                num_runs=NUM_RUNS,
                num_tasks_per_node=(num_tasks_per_node := 1),
                num_threads_per_task=7,
                partition=PARTITION,
                rocm_version=ROCM_VERSION,
                stack=STACK,
                stack_version=STACK_VERSION,
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
