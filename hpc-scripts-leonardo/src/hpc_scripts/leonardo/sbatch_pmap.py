#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import itertools
import os

from hpc_scripts import common
from hpc_scripts.leonardo import defaults, defs, make_run_pmap, sbatch

# >>> config: start
ACCOUNT: str = defaults.ACCOUNT
BRANCH: str = "leonardo"
DACE_DEFAULT_BLOCK_SIZE: str = ""
DRY_RUN: bool = False
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GT_BACKEND: list[str] = ["dace:gpu"]
JOB_ROOT_DIR: str = "_jobs"
NUM_RUNS: int = 10
PARTITION: defs.Partition = defaults.PARTITION
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = True
PMAP_ENABLE_OVERCOMPUTING: bool = True
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: list[defs.FloatingPointPrecision] = ["single"]
PYTHON_VERSION: defs.PythonVersion = "3.12"
QOS: str = "boost_qos_bprod"
REFRESH_PYTHON_VERSION: bool = False
SOFTWARE_STACK: defs.SoftwareStack = defaults.SOFTWARE_STACK
TIME: str = "01:00:00"
USE_CASE: dict[str, list[common.utils.ThreadsLayout]] = {
    # "baroclinic_wave_sphere_moist": [common.utils.ThreadsLayout(1, 1, 56)]
    # "weak-scaling/bomex-prescribed-boundary/leonardo/2": [common.utils.ThreadsLayout(1, 1, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/4": [common.utils.ThreadsLayout(1, 2, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/8": [common.utils.ThreadsLayout(1, 4, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/16": [common.utils.ThreadsLayout(2, 4, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/32": [common.utils.ThreadsLayout(4, 4, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/64": [common.utils.ThreadsLayout(8, 4, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/128": [common.utils.ThreadsLayout(16, 4, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/256": [common.utils.ThreadsLayout(32, 4, 8)],
    # "weak-scaling/bomex-prescribed-boundary/leonardo/512": [common.utils.ThreadsLayout(64, 4, 8)],
    "weak-scaling/bomex-prescribed-boundary/leonardo/1024": [common.utils.ThreadsLayout(128, 4, 8)],
    "weak-scaling/bomex-prescribed-boundary/leonardo/2048": [common.utils.ThreadsLayout(256, 4, 8)],
}
VERBOSE: bool = False
# >>> config: end


def main():
    for gt_backend, pmap_precision, use_case in itertools.product(
        GT_BACKEND, PMAP_PRECISION, USE_CASE
    ):
        for threads_layout in USE_CASE[use_case]:
            job_dir = os.path.join(
                JOB_ROOT_DIR,
                BRANCH,
                use_case,
                SOFTWARE_STACK,
                pmap_precision,
                gt_backend.replace(":", ""),
            )
            with common.utils.output_directory(path=job_dir) as output_dir:
                job_name = (
                    f"{use_case.replace('/', '-')}-{threads_layout.num_tasks}-{pmap_precision[0]}"
                )
                job_script = make_run_pmap.core(
                    branch=BRANCH,
                    dace_default_block_size=DACE_DEFAULT_BLOCK_SIZE,
                    ghex_aggregate_fields=GHEX_AGGREGATE_FIELDS,
                    ghex_collect_statistics=GHEX_COLLECT_STATISTICS,
                    gt_backend=gt_backend,
                    num_nodes=threads_layout.num_nodes,
                    num_runs=NUM_RUNS,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    num_threads_per_task=threads_layout.num_threads_per_task,
                    output_dir=output_dir,
                    pmap_disable_log=PMAP_DISABLE_LOG,
                    pmap_enable_benchmarking=PMAP_ENABLE_BENCHMARKING,
                    pmap_enable_overcomputing=PMAP_ENABLE_OVERCOMPUTING,
                    pmap_extended_timers=PMAP_EXTENDED_TIMERS,
                    pmap_precision=pmap_precision,
                    python_version=PYTHON_VERSION,
                    refresh_python_venv=REFRESH_PYTHON_VERSION,
                    software_stack=SOFTWARE_STACK,
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
                    qos=QOS,
                    time=TIME,
                    verbose=VERBOSE,
                )


if __name__ == "__main__":
    main()
