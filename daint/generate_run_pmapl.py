#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

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
PARTITION: defs.Partition = "gpu"
PMAP_ENABLE_BENCHMARKING: bool = False
PMAP_ENABLE_OVERCOMPUTING: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
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
    partition: defs.Partition,
    pmap_enable_benchmarking: bool,
    pmap_enable_overcomputing: bool,
    pmap_precision: defs.FloatingPointPrecision,
    use_case: str,
) -> str:
    prepare_pmap_fname = generate_prepare_pmap.core(branch, env, partition)

    with utils.batch_file(prefix="run_pmap") as (f, fname):
        utils.run(f". {prepare_pmap_fname}")

        with utils.chdir("$PMAP"):
            utils.run(f". venv/bin/activate")
            with utils.chdir("drivers"):
                utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
                utils.export_variable("GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics))
                utils.export_variable("GT_BACKEND", gt_backend)
                utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                utils.export_variable("OMP_PLACES", "cores")
                utils.export_variable("OMP_PROC_BIND", "close")
                utils.export_variable("PMAP_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking))
                utils.export_variable("PMAP_ENABLE_OVERCOMPUTING", int(pmap_enable_overcomputing))
                utils.export_variable("PMAP_PRECISION", pmap_precision)

                output_directory = os.path.join(
                    "$PWD",
                    use_case,
                    pmap_precision,
                    gt_backend.replace(":", ""),
                )
                utils.run(f"mkdir -p {output_directory}")
                command = (
                    f"CC=cc CXX=CC CUDA_HOST_CXX=CC "
                    f"srun --nodes={num_nodes} --ntasks-per-node={num_tasks_per_node} python run_model.py "
                    f"{os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_directory}"
                )
                if pmap_enable_benchmarking:
                    command += f" --performance-data-file={output_directory}/performance.csv"

                for _ in range(num_runs):
                    utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-enable-overcomputing", type=bool, default=PMAP_ENABLE_OVERCOMPUTING)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with utils.batch_directory():
        core(**args.__dict__)
