#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools

import defs
import generate_run_fvm
import sbatch
import utils


# >>> config: start
account: int = 465000527
branch_l: list[str] = ["main"]
partition_type: defs.PartitionType = "gpu"
env_l: list[defs.ProgrammingEnvironment] = ["cray"]
fvm_enable_benchmarking: bool = True
fvm_precision_l: list[defs.FloatingPointPrecision] = ["double"]
gt_backend_l: list[str] = ["dace:gpu"]
num_runs: int = 1
stack: defs.SoftwareStack = "lumi"
time: str = "00:30:00"
use_case_l: dict[str, list[utils.ThreadsLayout]] = {
    "weak-scaling/baroclinic-wave-sphere-moist/1": [utils.ThreadsLayout(1, 1, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/2": [utils.ThreadsLayout(1, 2, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/4": [utils.ThreadsLayout(1, 4, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/8": [utils.ThreadsLayout(1, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/16": [utils.ThreadsLayout(2, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/32": [utils.ThreadsLayout(4, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/64": [utils.ThreadsLayout(8, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/128": [utils.ThreadsLayout(16, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/256": [utils.ThreadsLayout(32, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/512": [utils.ThreadsLayout(64, 8, 1)],
    # "weak-scaling/baroclinic-wave-sphere-moist/1024": [utils.ThreadsLayout(128, 8, 1)],
}
# >>> config: end


def core():
    for branch, env, fvm_precision, gt_backend, use_case in itertools.product(
        branch_l, env_l, fvm_precision_l, gt_backend_l, use_case_l.keys()
    ):
        for threads_layout in use_case_l[use_case]:
            with utils.batch_directory():
                job_name = (
                    f"{use_case.replace('/', '_')}_{env}-{gt_backend}-{fvm_precision}-"
                    f"{threads_layout.num_nodes}-{threads_layout.num_tasks_per_node}"
                )
                job_script = generate_run_fvm.core(
                    branch=branch,
                    env=env,
                    fvm_enable_benchmarking=fvm_enable_benchmarking,
                    fvm_precision=fvm_precision,
                    gt_backend=gt_backend,
                    num_nodes=threads_layout.num_nodes,
                    num_runs=num_runs,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    num_threads_per_task=threads_layout.num_threads_per_task,
                    partition_type=partition_type,
                    stack=stack,
                    use_case=use_case,
                )
            sbatch.core(
                account=account,
                job_name=job_name,
                job_script=job_script,
                num_nodes=threads_layout.num_nodes,
                num_tasks_per_node=threads_layout.num_tasks_per_node,
                partition_type=partition_type,
                time=time,
            )


if __name__ == "__main__":
    core()
