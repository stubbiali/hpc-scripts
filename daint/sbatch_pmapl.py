#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools

import defs
import generate_run_pmapl
import sbatch
import utils


# >>> config: start
account: str = "s299"
branch_l: list[str] = ["benchmarking"]
partition: defs.Partition = "gpu"
env_l: list[defs.ProgrammingEnvironment] = ["gnu"]
ghex_aggregate_fields: bool = False
ghex_collect_statistics: bool = False
gt_backend_l: list[str] = [
    # "gt:cpu_kfirst",
    # "gt:cpu_ifirst",
    # "dace:cpu",
    # "cuda",
    # "gt:gpu",
    "dace:gpu",
]
num_runs: int = 10
pmap_disable_log: bool = False
pmap_enable_benchmarking: bool = True
pmap_enable_overcomputing_l: list[bool] = [True]
pmap_precision_l: list[defs.FloatingPointPrecision] = ["double"]
time: str = "02:00:00"
use_case_l: dict[str, list[utils.ThreadsLayout]] = {
    f"weak-scaling/bomex/{2**i}": [utils.ThreadsLayout(2**i, 1, 12)] for i in range(11)
}
# >>> config: end


def core():
    for (
        branch,
        env,
        gt_backend,
        pmap_enable_overcomputing,
        pmap_precision,
        use_case,
    ) in itertools.product(
        branch_l,
        env_l,
        gt_backend_l,
        pmap_enable_overcomputing_l,
        pmap_precision_l,
        use_case_l.keys(),
    ):
        for threads_layout in use_case_l[use_case]:
            for seed in range(6, 13):
                with utils.batch_directory():
                    # job_name = (
                    #     f"{use_case.replace('/', '_')}-{env}-{gt_backend}-{pmap_precision}-"
                    #     f"{pmap_enable_overcomputing}-{threads_layout.num_nodes}-"
                    #     f"{threads_layout.num_tasks_per_node}"
                    # )
                    # job_name = (
                    #     f"{gt_backend}-{pmap_precision}-"
                    #     f"{pmap_enable_overcomputing}-{threads_layout.num_nodes}-"
                    #     f"{threads_layout.num_tasks_per_node}"
                    # )
                    # job_name = f"{use_case[45:52]}-{gt_backend}-{pmap_precision}-{threads_layout.num_nodes}"
                    job_name = f"{use_case.replace('/', '-')}-{pmap_precision[0]}"
                    job_script = generate_run_pmapl.core(
                        branch=branch,
                        env=env,
                        ghex_aggregate_fields=ghex_aggregate_fields,
                        ghex_collect_statistics=ghex_collect_statistics,
                        gt_backend=gt_backend,
                        num_nodes=threads_layout.num_nodes,
                        num_runs=num_runs,
                        num_tasks_per_node=threads_layout.num_tasks_per_node,
                        num_threads_per_task=threads_layout.num_threads_per_task,
                        partition=partition,
                        pmap_disable_log=pmap_disable_log,
                        pmap_enable_benchmarking=pmap_enable_benchmarking,
                        pmap_enable_overcomputing=pmap_enable_overcomputing,
                        pmap_precision=pmap_precision,
                        use_case=use_case,
                    )
                sbatch.core(
                    account=account,
                    job_name=job_name,
                    job_script=job_script,
                    num_nodes=threads_layout.num_nodes,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    partition=partition,
                    time=time,
                )


if __name__ == "__main__":
    core()
