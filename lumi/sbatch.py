#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
import argparse
import importlib
import os
import typing

import update_path

import common_utils
import defaults
import defs
import utils


# >>> config: start
DRY_RUN: bool = False
JOB_NAME: str = "test_job"
JOB_SCRIPT: str = "test_job"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 8
TIME: str = "01:00:00"
# >>> config: end


def core(
    account: int,
    dry_run: bool,
    job_name: str,
    job_script: str,
    num_nodes: int,
    num_tasks_per_node: int,
    partition: defs.Partition,
    time: str,
    callback_module: typing.Optional[str] = None,
) -> None:
    if callback_module is not None:
        mod = importlib.import_module(callback_module)
        cb: typing.Callable[[], str] = getattr(mod, "callback", None)
        assert cb is not None, f"Module `{callback_module}` must define `callback()`."
        job_script = cb()

    with common_utils.batch_directory() as job_dir:
        error = os.path.join(job_dir, "error.txt")
        output = os.path.join(job_dir, "output.txt")
        with common_utils.batch_file(filename="batch") as (_, batch_file):
            command = [
                "sbatch",
                f"--account=project_{account}",
                f"--distribution=block:block",
                f"--error={error}",
                "--exclusive",
                f"--export=ALL",
                f"--job-name={job_name}",
                f"--nodes={num_nodes}",
                f"--ntasks-per-node={num_tasks_per_node}",
                f"--output={output}",
                f"--partition={partition}",
                f"--time={time}",
            ]
            if utils.get_partition_type(partition) == "gpu":
                command.append(f"--gpus-per-node=8")
            command.append(job_script)
            common_utils.run(*command, split=True)

    if not dry_run:
        common_utils.run(f". {batch_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit a batch job.")
    parser.add_argument("--account", type=int, default=defaults.ACCOUNT)
    parser.add_argument("--job-name", type=str, default=JOB_NAME)
    parser.add_argument("--job-script", type=str, default=JOB_SCRIPT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    parser.add_argument("--callback-module", type=str, default=None)
    args = parser.parse_args()
    core(**args.__dict__)
