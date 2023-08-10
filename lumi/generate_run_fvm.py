#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_prepare_fvm
import generate_prepare_mpi
import utils


# >>> config: start
BRANCH: str = "main"
ENV: defs.ProgrammingEnvironment = "cray"
FVM_ENABLE_BENCHMARKING: bool = False
FVM_PRECISION: defs.FloatingPointPrecision = "double"
GT_BACKEND: str = "dace:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
USE_CASE: str = "thermal"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    fvm_enable_benchmarking: bool,
    fvm_precision: defs.FloatingPointPrecision,
    gt_backend: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
    use_case: str,
) -> str:
    prepare_fvm_fname = generate_prepare_fvm.core(branch, env, partition_type, stack)
    prepare_mpi_fname = generate_prepare_mpi.core(partition_type)

    with utils.batch_file(prefix="run_fvm") as (f, fname):
        utils.run(f". {prepare_fvm_fname}")
        utils.run(f". {prepare_mpi_fname}")

        with utils.chdir("$FVM"):
            utils.run(f". venv/{env}/bin/activate")
            with utils.chdir("drivers"):
                utils.export_variable("FVM_ENABLE_BENCHMARKING", int(fvm_enable_benchmarking))
                utils.export_variable("FVM_PRECISION", fvm_precision)
                utils.export_variable("GT_BACKEND", gt_backend)
                utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                utils.export_variable("OMP_PLACES", "cores")
                utils.export_variable("OMP_PROC_BIND", "close")

                srun_options = utils.get_srun_options(
                    num_nodes, num_tasks_per_node, num_threads_per_task, partition_type
                )
                output_directory = os.path.join(
                    "$PWD", "data", gt_backend.replace(":", ""), fvm_precision, use_case
                )
                utils.run(f"mkdir -p {output_directory}")
                command = (
                    f"srun {' '.join(srun_options)} ./../../../select_gpu.sh python run_model.py "
                    f"{os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_directory}"
                )
                if fvm_enable_benchmarking:
                    command += f" --performance-data-file={output_directory}/performance.csv"

                for _ in range(num_runs):
                    utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--fvm-enable-benchmarking", type=bool, default=FVM_ENABLE_BENCHMARKING)
    parser.add_argument("--fvm-precision", type=str, default=FVM_PRECISION)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with utils.batch_directory():
        core(**args.__dict__)
