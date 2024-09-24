#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import typing

import defs
import generate_prepare_fvm
import generate_prepare_mpi
import utils


# >>> config: start
BRANCH: str = "main"
ENV: defs.ProgrammingEnvironment = "cray"
GT_BACKEND: str = "dace:gpu"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 8
NUM_THREADS_PER_TASK: int = 1
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    gt_backend: str,
    num_nodes: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
) -> str:
    prepare_fvm_fname = generate_prepare_fvm.core(branch, env, partition_type, stack)
    prepare_mpi_fname = generate_prepare_mpi.core(partition_type)

    with utils.batch_file(prefix="test_binding") as (f, fname):
        utils.run(f". {prepare_fvm_fname}")
        utils.run(f". {prepare_mpi_fname}")

        with utils.chdir("$FVM"):
            utils.run(f". venv/{env}/bin/activate")
            with utils.chdir("tests/distributed"):
                utils.export_variable("GT_BACKEND", gt_backend)
                srun_options = utils.get_srun_options(
                    num_nodes, num_tasks_per_node, num_threads_per_task, partition_type
                )
                utils.run(
                    f"srun {' '.join(srun_options)} ./../../../../select_gpu.sh "
                    f"python test_binding.py"
                )

    return fname


def callback():
    with utils.batch_directory():
        fname = core(
            branch=BRANCH,
            env=ENV,
            gt_backend=GT_BACKEND,
            num_nodes=NUM_NODES,
            num_tasks_per_node=NUM_TASKS_PER_NODE,
            num_threads_per_task=NUM_THREADS_PER_TASK,
            partition_type=PARTITION_TYPE,
            stack=STACK,
        )
    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test process binding to hardware.")
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    args = parser.parse_args()
    with utils.batch_directory():
        core(**args.__dict__)
