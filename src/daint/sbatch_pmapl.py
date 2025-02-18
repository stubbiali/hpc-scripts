#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools
import os
import typing

import update_path  # noqa: F401

import common.utils as common_utils
import defs
import make_run_pmapl
import sbatch


# >>> config: start
# account to be used to submit the jobs
ACCOUNT: str = "s299"

# branch of the PMAP-L repository
BRANCH: str = "benchmarking"

# True to ask for contiguous nodes
CONTIGUOUS_NODES: bool = False

# True to copy the GT4Py cache directory to /dev/shm before running the model
# this is still experimental, but might help job startup time at high node counts
COPY_GT_CACHE_TO_DEV_SHM: bool = False

# True to copy the GT4Py cache directory to /tmp before running the model
# this is still experimental, but might help job startup time at high node counts
COPY_GT_CACHE_TO_TMP: bool = False

# True to generate the scripts only, without submitting any job
DRY_RUN: bool = True

# True to profile the code using cProfile
ENABLE_CPROFILE: bool = False

# partition of Piz Daint
PARTITION: defs.Partition = "mc"

# programming environment
ENV: defs.ProgrammingEnvironment = "gnu"

# value of the env variable GHEX_AGGREGATE_FIELDS
GHEX_AGGREGATE_FIELDS: bool = False

# value of the env variable GHEX_COLLECT_STATISTICS
GHEX_COLLECT_STATISTICS: bool = False

# transport backend for GHEX
GHEX_TRANSPORT_BACKEND: defs.GHEXTransportBackend = "mpi"

# list of GT4Py backends to be used
GT_BACKEND: list[str] = [
    "gt:cpu_kfirst",
    # "gt:cpu_ifirst",
    # "dace:cpu",
    # "cuda",
    # "gt:gpu",
    # "dace:gpu"
]

# folder (relative to the current directory) where scripts will be placed
JOB_ROOT_DIR: str = "bomex-prescribed-boundary-noswitch"

# number of model runs to perform
NUM_RUNS: int = 3

# value of the env variable FVM_DISABLE_LOG
PMAP_DISABLE_LOG: bool = False

# value of the env variable FVM_ENABLE_BENCHMARKING
PMAP_ENABLE_BENCHMARKING: bool = True

# value of the env variable FVM_ENABLE_OVERCOMPUTING
PMAP_ENABLE_OVERCOMPUTING: bool = True

# value of the env variable FVM_EXTENDED_TIMERS
PMAP_EXTENDED_TIMERS: bool = False

# values of the env variable FVM_PRECISION
PMAP_PRECISION: list[defs.FloatingPointPrecision] = ["double", "single"]

# the model source code is assumed to be found under PMAP_ROOT_DIR/pmapl/BRANCH
# if not otherwise specified, PMAP_ROOT_DIR is the current directory
PMAP_ROOT_DIR: typing.Optional[str] = None

# jobs reservation (if any)
RESERVATION: typing.Optional[str] = None

# True to ask the scheduler to minimize the number of electrical groups spanned by the allocated nodes
SET_SWITCHES: bool = False

# job time limit
TIME: str = "01:00:00"

# list of use cases
USE_CASE: dict[str, list[common_utils.ThreadsLayout]] = {
    # **{
    #     f"weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/128x128/{num_nodes}": [
    #         common_utils.ThreadsLayout(num_nodes, 1, 12)
    #     ]
    #     for num_nodes in (1, 4, 16, 64, 256, 1024, 4096)
    # },
    # **{
    #     f"weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/160x160/{num_nodes}": [
    #         common_utils.ThreadsLayout(num_nodes, 1, 12)
    #     ]
    #     for num_nodes in (1, 4, 16, 64, 256, 1024, 4096)
    # },
    # **{
    #     f"weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/256x256/{num_nodes}": [
    #         common_utils.ThreadsLayout(num_nodes, 1, 12)
    #     ]
    #     for num_nodes in (1, 4, 16, 64, 256, 1024, 4096)
    # },
    # **{
    #     f"weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-tracer/128x128/{num_nodes}": [
    #         common_utils.ThreadsLayout(num_nodes, 1, 12)
    #     ]
    #     for num_nodes in (1, 4, 16, 64, 256, 1024, 4096)
    # },
    # **{
    #     f"weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-tracer/160x160/{num_nodes}": [
    #         common_utils.ThreadsLayout(num_nodes, 1, 12)
    #     ]
    #     for num_nodes in (1, 4, 16, 64, 256, 1024, 4096)
    # },
    # **{
    #     f"weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-tracer/256x256/{num_nodes}": [
    #         common_utils.ThreadsLayout(num_nodes, 1, 12)
    #     ]
    #     for num_nodes in (1, 4, 16, 64, 256, 1024, 4096)
    # },
    **{
        f"weak-scaling/bomex-prescribed-boundary/{num_nodes}": [
            common_utils.ThreadsLayout(num_nodes, 1, 36)
        ]
        for num_nodes in (1, 2, 4, 8, 12, 16, 32, 64, 128, 256, 512, 1024)
    },
    # **{
    #     f"weak-scaling/bomex/{num_nodes}": [common_utils.ThreadsLayout(num_nodes, 1, 12)]
    #     for num_nodes in (1, 4, 16, 64)  # , 256, 1024, 4096)
    # },
    # "weak-scaling/bomex-prescribed-boundary/1": [common_utils.ThreadsLayout(1, 1, 12)],
    # "weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/256x256/1": [
    #     common_utils.ThreadsLayout(1, 1, 12)
    # ],
    # "weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/256x256/1": [
    #     common_utils.ThreadsLayout(1, 1, 12)
    # ],
    # "weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/256x256/4": [
    #     common_utils.ThreadsLayout(4, 1, 12)
    # ],
    # "weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/256x256/8": [
    #     common_utils.ThreadsLayout(8, 1, 12)
    # ],
    # "weak-scaling/fuhrer-et-al-gmd-2018/baroclinic-wave-sphere-dry/256x256/256": [
    #     common_utils.ThreadsLayout(256, 1, 12)
    # ],
    # "weak-scaling/baroclinic-wave-sphere-moist-mpdata-vector/1": [common_utils.ThreadsLayout(1, 1, 12)],
}
# >>> config: end


def core():
    for gt_backend, pmap_precision, use_case in itertools.product(
        GT_BACKEND, PMAP_PRECISION, USE_CASE
    ):
        for threads_layout in USE_CASE[use_case]:
            job_dir = os.path.join(
                JOB_ROOT_DIR, BRANCH, use_case, pmap_precision, gt_backend.replace(":", "")
            )
            with common_utils.batch_directory(path=job_dir) as output_dir:
                job_name = (
                    f"{use_case.replace('/', '_')}-{gt_backend}-{pmap_precision[0]}-"
                    f"{threads_layout.num_nodes}-"
                )
                job_script = make_run_pmapl.core(
                    branch=BRANCH,
                    copy_gt_cache_to_dev_shm=COPY_GT_CACHE_TO_DEV_SHM,
                    copy_gt_cache_to_tmp=COPY_GT_CACHE_TO_TMP,
                    enable_cprofile=ENABLE_CPROFILE,
                    env=ENV,
                    ghex_aggregate_fields=GHEX_AGGREGATE_FIELDS,
                    ghex_collect_statistics=GHEX_COLLECT_STATISTICS,
                    ghex_transport_backend=GHEX_TRANSPORT_BACKEND,
                    gt_backend=gt_backend,
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
                    root_dir=PMAP_ROOT_DIR,
                    use_case=use_case,
                )
                sbatch.core(
                    account=ACCOUNT,
                    contiguous_nodes=CONTIGUOUS_NODES,
                    dry_run=DRY_RUN,
                    job_name=job_name,
                    job_script=job_script,
                    num_nodes=threads_layout.num_nodes,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    partition=PARTITION,
                    reservation=RESERVATION,
                    set_switches=SET_SWITCHES,
                    time=TIME,
                )


if __name__ == "__main__":
    core()
