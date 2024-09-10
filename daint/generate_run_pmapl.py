#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
import typing

import defs
import generate_prepare_pmapl
import utils


# >>> config: start
BRANCH: str = "main"
ENV: defs.ProgrammingEnvironment = "gnu"
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GT_BACKEND: str = "dace:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
OUTPUT_DIR: typing.Optional[str] = None
PARTITION: defs.Partition = "gpu"
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = False
PMAP_ENABLE_OVERCOMPUTING: bool = False
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
ROOT_DIR: typing.Optional[str] = None
USE_CASE: str = "thermal"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    gt_backend: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    output_dir: str,
    partition: defs.Partition,
    pmap_disable_log: bool,
    pmap_enable_benchmarking: bool,
    pmap_enable_overcomputing: bool,
    pmap_extended_timers: bool,
    pmap_precision: defs.FloatingPointPrecision,
    root_dir: typing.Optional[str],
    use_case: str,
) -> str:
    prepare_pmapl_fname = generate_prepare_pmapl.core(branch, env, partition, root_dir)

    with utils.batch_file(filename="run_pmapl") as (f, fname):
        utils.run(f". {prepare_pmapl_fname}")

        with utils.chdir("$PMAPL"):
            with utils.chdir("drivers"):
                utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
                utils.export_variable("GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics))
                utils.export_variable("GT_BACKEND", gt_backend)
                utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                utils.export_variable("OMP_PLACES", "cores")
                utils.export_variable("OMP_PROC_BIND", "close")
                utils.export_variable("FVM_DISABLE_LOG", int(pmap_disable_log))
                utils.export_variable("FVM_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking))
                utils.export_variable("FVM_ENABLE_OVERCOMPUTING", int(pmap_enable_overcomputing))
                utils.export_variable("FVM_EXTENDED_TIMERS", int(pmap_extended_timers))
                utils.export_variable("FVM_PRECISION", pmap_precision)
                # utils.export_variable("CUDA_LAUNCH_BLOCKING", 1)

                if output_dir is not None:
                    output_dir = os.path.abspath(output_dir)
                else:
                    output_dir = os.path.join(
                        "$PWD", use_case, pmap_precision, gt_backend.replace(":", "")
                    )
                utils.run(f"mkdir -p {output_dir}")
                command = (
                    f"CC=cc CXX=CC "
                    f"{'CUDA_HOST_CXX=CC' if gt_backend in ('dace:gpu', 'gt:gpu') else ''} "
                    f"srun --nodes={num_nodes} --ntasks-per-node={num_tasks_per_node} "
                    f"python run_model.py {os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_dir}"
                )
                if pmap_disable_log or pmap_enable_benchmarking:
                    command += " --write-profiling-data"

                for _ in range(num_runs):
                    utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--pmap-disable-log", type=bool, default=PMAP_DISABLE_LOG)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-enable-overcomputing", type=bool, default=PMAP_ENABLE_OVERCOMPUTING)
    parser.add_argument("--pmap-extended-timers", type=bool, default=PMAP_EXTENDED_TIMERS)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with utils.batch_directory():
        core(**args.__dict__)
