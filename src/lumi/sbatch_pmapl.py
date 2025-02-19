#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools
import os
from typing import TYPE_CHECKING

import common.utils
import defaults
import make_run_pmapl
import sbatch

if TYPE_CHECKING:
    import defs


# >>> config: start
ACCOUNT: int = defaults.ACCOUNT
BRANCH: str = "benchmarking-lumi"
DACE_DEFAULT_BLOCK_SIZE: str = "'256,1,1'"
DRY_RUN: bool = True
ENV: defs.ProgrammingEnvironment = "cray"
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GHEX_TRANSPORT_BACKEND: defs.GHEXTransportBackend = "mpi"
GT_BACKEND: list[str] = ["gt:gpu"]
JOB_ROOT_DIR: str = "bomex-prescribed-boundary"
HDF5_VERSION: str = defaults.HDF5_VERSION
NETCDF_VERSION: str = defaults.NETCDF_VERSION
NUM_RUNS: int = 10
PARTITION: defs.Partition = "standard-g"
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = True
PMAP_ENABLE_OVERCOMPUTING: bool = True
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: list[defs.FloatingPointPrecision] = ["single"]
ROCM_VERSION: str = defaults.ROCM_VERSION
STACK: defs.SoftwareStack = defaults.STACK
STACK_VERSION: str = defaults.STACK_VERSION
TIME: str = "00:45:00"
USE_CASE: dict[str, list[common.utils.ThreadsLayout]] = {
    "weak-scaling/bomex-prescribed-boundary/4": [common.utils.ThreadsLayout(1, 1, 7)],
    "weak-scaling/bomex-prescribed-boundary/8": [common.utils.ThreadsLayout(1, 2, 7)],
    "weak-scaling/bomex-prescribed-boundary/16": [common.utils.ThreadsLayout(1, 4, 7)],
    "weak-scaling/bomex-prescribed-boundary/32": [common.utils.ThreadsLayout(1, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/64": [common.utils.ThreadsLayout(2, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/128": [common.utils.ThreadsLayout(4, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/256": [common.utils.ThreadsLayout(8, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/512": [common.utils.ThreadsLayout(16, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/1024": [common.utils.ThreadsLayout(32, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/2048": [common.utils.ThreadsLayout(64, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/4096": [common.utils.ThreadsLayout(128, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/8192": [common.utils.ThreadsLayout(256, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/16384": [common.utils.ThreadsLayout(512, 8, 7)],
}
# >>> config: end


def core():
    for gt_backend, pmap_precision, use_case in itertools.product(
        GT_BACKEND, PMAP_PRECISION, USE_CASE
    ):
        for threads_layout in USE_CASE[use_case]:
            job_dir = os.path.join(
                JOB_ROOT_DIR,
                BRANCH,
                use_case,
                pmap_precision,
                GHEX_TRANSPORT_BACKEND,
                gt_backend.replace(":", ""),
            )
            with common.utils.batch_directory(path=job_dir) as output_dir:
                job_name = (
                    f"{use_case.replace('/', '-')}-{threads_layout.num_tasks}-{pmap_precision[0]}"
                )
                job_script = make_run_pmapl.core(
                    branch=BRANCH,
                    dace_default_block_size=DACE_DEFAULT_BLOCK_SIZE,
                    env=ENV,
                    ghex_aggregate_fields=GHEX_AGGREGATE_FIELDS,
                    ghex_collect_statistics=GHEX_COLLECT_STATISTICS,
                    ghex_transport_backend=GHEX_TRANSPORT_BACKEND,
                    gt_backend=gt_backend,
                    hdf5_version=HDF5_VERSION,
                    netcdf_version=NETCDF_VERSION,
                    num_nodes=threads_layout.num_nodes,
                    num_runs=NUM_RUNS,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    num_threads_per_task=threads_layout.num_threads_per_task,
                    output_dir=output_dir,
                    partition=PARTITION,
                    pmap_disable_log=PMAP_DISABLE_LOG,
                    pmap_enable_benchmarking=PMAP_ENABLE_BENCHMARKING,
                    pmap_enable_overcomputing=PMAP_ENABLE_OVERCOMPUTING,
                    pmap_extended_timers=PMAP_EXTENDED_TIMERS,
                    pmap_precision=pmap_precision,
                    rocm_version=ROCM_VERSION,
                    stack=STACK,
                    stack_version=STACK_VERSION,
                    use_case=use_case,
                )
                sbatch.core(
                    account=ACCOUNT,
                    dry_run=DRY_RUN,
                    job_name=job_name,
                    job_script=job_script,
                    num_nodes=threads_layout.num_nodes,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    partition=PARTITION,
                    time=TIME,
                )


if __name__ == "__main__":
    core()
