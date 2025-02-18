#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools
import os
from typing import Literal, Optional

import common.utils
import defs
import make_run_pmap
import sbatch


# >>> config: start
ARGS = {
    "account": "bd1069",
    "branch": "main",
    "compiler": "nvhpc@24.7",
    "dace_default_block_size": "",
    "dry_run": True,
    "ghex_aggregate_fields": False,
    "ghex_collect_statistics": False,
    "gt_backend_list": ["gt:gpu"],
    "gt_backend_list": ["dace:gpu"],
    "job_root_dir": "_jobs",
    "mpi": "openmpi@4.1.5",
    "num_runs": 1,
    "partition": "gpu",
    "pmap_disable_log": False,
    "pmap_enable_benchmarking": True,
    "pmap_extended_timers": False,
    "pmap_precision_list": ["double", "single"],
    "python": "python@3.11",
    "reservation": None,
    "time": "01:00:00",
    "use_case_dict": {
        "weak-scaling/baroclinic-wave-sphere-moist/1": [common.utils.ThreadsLayout(1, 1, 1)]
    },
}
# >>> config: end


def core(
    account: str,
    branch: str,
    compiler: defs.Compiler,
    dace_default_block_size: str,
    dry_run: bool,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    gt_backend_list: list[str],
    job_root_dir: str,
    mpi: defs.MPI,
    num_runs: int,
    partition: defs.Partition,
    pmap_disable_log: bool,
    pmap_enable_benchmarking: bool,
    pmap_extended_timers: bool,
    pmap_precision_list: list[defs.FloatingPointPrecision],
    python: defs.Python,
    reservation: Optional[str],
    time: str,
    use_case_dict: dict[str, list[common.utils.ThreadsLayout]],
    project_name: Literal["pmap-les", "pmap-les-dlr"],
) -> None:
    for gt_backend, pmap_precision, use_case in itertools.product(
        gt_backend_list, pmap_precision_list, use_case_dict
    ):
        job_dir = os.path.join(
            job_root_dir,
            project_name,
            branch,
            use_case,
            pmap_precision,
            gt_backend.replace(":", ""),
        )
        for threads_layout in use_case_dict[use_case]:
            with common.utils.batch_directory(path=job_dir) as output_dir:
                job_name = (
                    f"{use_case.replace('/', '_')}-{gt_backend}-{pmap_precision[0]}-"
                    f"{threads_layout.num_nodes * threads_layout.num_tasks_per_node}"
                )
                job_script = make_run_pmap.core(
                    branch=branch,
                    compiler=compiler,
                    dace_default_block_size=dace_default_block_size,
                    ghex_aggregate_fields=ghex_aggregate_fields,
                    ghex_collect_statistics=ghex_collect_statistics,
                    gt_backend=gt_backend,
                    mpi=mpi,
                    num_nodes=threads_layout.num_nodes,
                    num_runs=num_runs,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    num_threads_per_task=threads_layout.num_threads_per_task,
                    output_dir=output_dir,
                    partition=partition,
                    pmap_disable_log=pmap_disable_log,
                    pmap_enable_benchmarking=pmap_enable_benchmarking,
                    pmap_extended_timers=pmap_extended_timers,
                    pmap_precision=pmap_precision,
                    python=python,
                    use_case=use_case,
                    project_name=project_name,
                )
                sbatch.core(
                    account=account,
                    dry_run=dry_run,
                    job_name=job_name,
                    job_script=job_script,
                    num_nodes=threads_layout.num_nodes,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    partition=partition,
                    reservation=reservation,
                    time=time,
                )


if __name__ == "__main__":
    core(**ARGS, project_name="pmap-les")
