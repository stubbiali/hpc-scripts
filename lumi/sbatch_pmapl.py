#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import itertools

import defs
import generate_run_pmapl
import sbatch
import utils


# >>> config: start
account: int = 465000527
branch_l: list[str] = ["benchmarking"]
compiler_version: str = "16.0.1"
default_block_size: str = "'256,1,1'"
env: defs.ProgrammingEnvironment = "cray"
env_version: str = "8.4.0"
ghex_aggregate_fields: bool = False
ghex_collect_statistics: bool = False
gt_backend_l: list[str] = ["gt:gpu"]
hdf5_version: str = "1.14.4.3"
netcdf_version: str = "4.9.2"
num_runs: int = 10
partition_type: defs.PartitionType = "gpu"
pmap_enable_benchmarking: bool = True
pmap_enable_overcomputing_l: list[bool] = [True]
pmap_precision_l: list[defs.FloatingPointPrecision] = ["double"]
stack: defs.SoftwareStack = "lumi"
stack_version: str = "23.09"
time: str = "01:30:00"
# use_case_l: dict[str, list[utils.ThreadsLayout]] = {
#     "baroclinic_wave_sphere_moist_mpdata": [utils.ThreadsLayout(1, 1, 56)],
#     "baroclinic_wave_sphere_moist": [utils.ThreadsLayout(1, 1, 56)],
# }
use_case_l: dict[str, list[utils.ThreadsLayout]] = {
    "weak-scaling/bomex-prescribed-boundary/1": [utils.ThreadsLayout(1, 1, 7)],
    "weak-scaling/bomex-prescribed-boundary/2": [utils.ThreadsLayout(1, 2, 7)],
    "weak-scaling/bomex-prescribed-boundary/4": [utils.ThreadsLayout(1, 4, 7)],
    "weak-scaling/bomex-prescribed-boundary/8": [utils.ThreadsLayout(1, 8, 7)],
    "weak-scaling/bomex-prescribed-boundary/16": [utils.ThreadsLayout(2, 8, 7)],
    # "weak-scaling/bomex-prescribed-boundary/32": [utils.ThreadsLayout(4, 8, 7)],
    # "weak-scaling/bomex-prescribed-boundary/64": [utils.ThreadsLayout(8, 8, 7)],
    # "weak-scaling/bomex-prescribed-boundary/128": [utils.ThreadsLayout(16, 8, 7)],
    # "weak-scaling/bomex-prescribed-boundary/256": [utils.ThreadsLayout(32, 8, 7)],
    # "weak-scaling/bomex-prescribed-boundary/512": [utils.ThreadsLayout(64, 8, 7)],
}
# use_case_l: dict[str, list[utils.ThreadsLayout]] = {
# "weak-scaling/baroclinic-wave-sphere-moist/1": [utils.ThreadsLayout(1, 1, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/2": [utils.ThreadsLayout(1, 2, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/4": [utils.ThreadsLayout(1, 4, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/8": [utils.ThreadsLayout(1, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/16": [utils.ThreadsLayout(2, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/32": [utils.ThreadsLayout(4, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/64": [utils.ThreadsLayout(8, 8, 7)],
# "baroclinic_wave_sphere_moist_pasc_poster": [utils.ThreadsLayout(8, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/128": [utils.ThreadsLayout(16, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/256": [utils.ThreadsLayout(32, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/512": [utils.ThreadsLayout(64, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/1024": [utils.ThreadsLayout(128, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/2048": [utils.ThreadsLayout(256, 8, 7)],
# "weak-scaling/baroclinic-wave-sphere-moist/4096": [utils.ThreadsLayout(512, 8, 1)],
# "weak-scaling/baroclinic-wave-sphere-moist/16384": [utils.ThreadsLayout(2048, 8, 1)],
# }
# use_case_l: dict[str, list[utils.ThreadsLayout]] = {
# "weak-scaling/baroclinic-wave-sphere-moist/1": [utils.ThreadsLayout(1, 1, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/2": [utils.ThreadsLayout(1, 2, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/4": [utils.ThreadsLayout(1, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/8": [utils.ThreadsLayout(2, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/16": [utils.ThreadsLayout(4, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/32": [utils.ThreadsLayout(8, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/64": [utils.ThreadsLayout(16, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/128": [utils.ThreadsLayout(32, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/256": [utils.ThreadsLayout(64, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/512": [utils.ThreadsLayout(128, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/1024": [utils.ThreadsLayout(256, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/2048": [utils.ThreadsLayout(512, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/4096": [utils.ThreadsLayout(1024, 4, 14)],
# "weak-scaling/baroclinic-wave-sphere-moist/16384": [utils.ThreadsLayout(4096, 4, 14)],
# }
# >>> config: end


def core():
    for (
        branch,
        gt_backend,
        pmap_enable_overcomputing,
        pmap_precision,
        use_case,
    ) in itertools.product(
        branch_l,
        gt_backend_l,
        pmap_enable_overcomputing_l,
        pmap_precision_l,
        use_case_l.keys(),
    ):
        for threads_layout in use_case_l[use_case]:
            with utils.batch_directory():
                # job_name = (
                #     f"{use_case.replace('/', '_')}-{env}-{gt_backend}-{pmap_precision}-"
                #     f"{pmap_enable_overcomputing}-{threads_layout.num_nodes}-"
                #     f"{threads_layout.num_tasks_per_node}"
                # )
                # job_name = (
                #     f"{gt_backend}-{pmap_precision}-"
                #     f"oc{int(pmap_enable_overcomputing)}-{threads_layout.num_nodes}-"
                #     f"{threads_layout.num_tasks_per_node}"
                # )
                # job_name = f"{gt_backend}-{pmap_precision}"
                job_name = (
                    f"{use_case.replace('/', '-')}-{pmap_precision[0]}"
                )
                job_script = generate_run_pmapl.core(
                    branch=branch,
                    compiler_version=compiler_version,
                    default_block_size=default_block_size,
                    env=env,
                    env_version=env_version,
                    ghex_aggregate_fields=ghex_aggregate_fields,
                    ghex_collect_statistics=ghex_collect_statistics,
                    gt_backend=gt_backend,
                    hdf5_version=hdf5_version,
                    netcdf_version=netcdf_version,
                    num_nodes=threads_layout.num_nodes,
                    num_runs=num_runs,
                    num_tasks_per_node=threads_layout.num_tasks_per_node,
                    num_threads_per_task=threads_layout.num_threads_per_task,
                    partition_type=partition_type,
                    pmap_enable_benchmarking=pmap_enable_benchmarking,
                    pmap_enable_overcomputing=pmap_enable_overcomputing,
                    pmap_precision=pmap_precision,
                    stack=stack,
                    stack_version=stack_version,
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
