#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
import argparse
import importlib
import os
import typing

import defs
import utils


# >>> config: start
ACCOUNT: int = 465000527
JOB_NAME: str = "test_job"
JOB_SCRIPT: str = "test_job"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 8
PARTITION_TYPE: defs.PartitionType = "gpu"
TIME: str = "00:02:00"
# >>> config: end


def core(
    account: int,
    job_name: str,
    job_script: str,
    num_nodes: int,
    num_tasks_per_node: int,
    partition_type: defs.PartitionType,
    time: str,
    callback_module: typing.Optional[str] = None,
) -> None:
    os.makedirs("_error", exist_ok=True)
    os.makedirs("_output", exist_ok=True)

    if callback_module is not None:
        mod = importlib.import_module(callback_module)
        cb: typing.Callable[[], str] = getattr(mod, "callback", None)
        assert cb is not None, f"Module `{callback_module}` must define `callback()`."
        job_script = cb()

    command = [
        "sbatch",
        f"--account=project_{account}",
        f"--distribution=block:block",
        f"--error=_error/{job_name}.err",
        f"--export=ALL",
        f"--job-name={job_name}",
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        f"--output=_output/{job_name}.out",
        f"--partition={utils.get_partition(partition_type)}",
        f"--time={time}",
    ]
    if partition_type == "gpu":
        command.append(f"--gpus-per-node=8")
    command.append(job_script)
    utils.run(*command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit a batch job.")
    parser.add_argument("--account", type=int, default=ACCOUNT)
    parser.add_argument("--job-name", type=str, default=JOB_NAME)
    parser.add_argument("--job-script", type=str, default=JOB_SCRIPT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--time", type=str, default=TIME)
    parser.add_argument("--callback-module", type=str, default=None)
    args = parser.parse_args()
    core(**args.__dict__)
