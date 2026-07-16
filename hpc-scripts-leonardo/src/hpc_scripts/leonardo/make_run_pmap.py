#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os

from hpc_scripts import common
from hpc_scripts.leonardo import defaults, defs, make_prepare_pmap, make_select_gpu

# >>> config: start
BRANCH: str = "leonardo"
DACE_DEFAULT_BLOCK_SIZE: str = ""
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GT_BACKEND: str = "dace:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 2
NUM_THREADS_PER_TASK: int = 8
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = True
PMAP_ENABLE_OVERCOMPUTING: bool = True
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
USE_CASE: str = "weak-scaling/bomex-prescribed-boundary/lumi/2"
# >>> config: end


def core(
    branch: str,
    dace_default_block_size: str,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    gt_backend: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    output_dir: str,
    pmap_disable_log: bool,
    pmap_enable_benchmarking: bool,
    pmap_enable_overcomputing: bool,
    pmap_extended_timers: bool,
    pmap_precision: defs.FloatingPointPrecision,
    python_version: defs.PythonVersion,
    refresh_python_venv: bool,
    software_stack: defs.SoftwareStack,
    use_case: str,
) -> str:
    prepare_pmap_fname = make_prepare_pmap.core(
        branch, software_stack, python_version, refresh_python_venv
    )

    with common.utils.output_file(filename="run_pmap") as (_, fname):
        common.utils.run(f". {prepare_pmap_fname}")

        with common.utils.chdir("$PMAP"):
            common.utils.run(". $PMAP_VENV/bin/activate")
            common.utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
            common.utils.export_variable("GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics))
            common.utils.export_variable("GT_BACKEND", gt_backend)
            common.utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
            common.utils.export_variable("OMP_PLACES", "cores")
            common.utils.export_variable("OMP_PROC_BIND", "close")
            # common.utils.export_variable("OMP_DISPLAY_AFFINITY", "True")
            common.utils.export_variable("PMAP_DISABLE_LOG", int(pmap_disable_log))
            common.utils.export_variable("PMAP_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking))
            common.utils.export_variable(
                "PMAP_ENABLE_OVERCOMPUTING", int(pmap_enable_overcomputing)
            )
            common.utils.export_variable("PMAP_EXTENDED_TIMERS", int(pmap_extended_timers))
            common.utils.export_variable("PMAP_PRECISION", pmap_precision)
            if dace_default_block_size:
                common.utils.export_variable("DACE_DEFAULT_BLOCK_SIZE", dace_default_block_size)

            if output_dir is not None:
                output_dir = os.path.abspath(output_dir)
            else:
                output_dir = os.path.join(
                    "_data", software_stack, use_case, pmap_precision, gt_backend.replace(":", "")
                )
            common.utils.run(f"mkdir -p {output_dir}")
            select_gpu_fname = make_select_gpu.core()
            command = (
                f"srun "
                f"--nodes={num_nodes} --ntasks-per-node={num_tasks_per_node} "
                f"--cpu-bind=ldoms --gpus-per-task=1 --gpu-bind=none "
                f"{select_gpu_fname} pmap {os.path.join('config', use_case + '.yml')} "
                f"--output-directory={output_dir}"
            )
            if pmap_enable_benchmarking:
                command += " --write-profiling-data"

            for _ in range(num_runs):
                common.utils.run(command)

    return fname


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--dace-default-block-size", type=str, default=DACE_DEFAULT_BLOCK_SIZE)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--pmap-disable-log", type=bool, default=PMAP_DISABLE_LOG)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-enable-overcomputing", type=bool, default=PMAP_ENABLE_OVERCOMPUTING)
    parser.add_argument("--pmap-extended-timers", type=bool, default=PMAP_EXTENDED_TIMERS)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--python-version", type=str, default=defaults.PYTHON_VERSION)
    parser.add_argument("--refresh-python-venv", action="store_true")
    parser.add_argument("--software-stack", type=str, default=defaults.SOFTWARE_STACK)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with common.utils.output_directory() as output_dir:
        core(**args.__dict__, output_dir=output_dir)


if __name__ == "__main__":
    main()
