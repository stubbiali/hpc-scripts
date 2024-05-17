#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
import argparse
import importlib
import os
import typing

import defs
import utils


# >>> config: start
project_id="$(sacct --format=Account --noheader | head -n 1 | awk '{$1=$1}1')"
ACCOUNT: str = project_id
JOB_NAME: str = "test_job"
JOB_SCRIPT: str = "test_job"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 1
PARTITION: defs.Partition = "gpu"
TIME: str = "01:00:00"
# >>> config: end


def core(
    account: str,
    job_name: str,
    job_script: str,
    num_nodes: int,
    num_tasks_per_node: int,
    partition: defs.Partition,
    time: str,
    *,
    callback_module: typing.Optional[str] = None,
    contiguous: bool = False,
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
        f"--account={account}{'m' if partition == 'mc' else ''}",
        f"--constraint={partition}",
        f"--distribution=block",
        f"--error=_error/{job_name}.err",
        f"--exclusive",
        f"--export=ALL",
        f"--job-name={job_name}",
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        f"--output=_output/{job_name}.out",
        f"--partition=normal",
        f"--time={time}",
    ]
    if contiguous:
        command.append(f"--contiguous")
    command.append(job_script)
    utils.run(*command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit a batch job.")
    parser.add_argument("--account", type=str, default=ACCOUNT)
    parser.add_argument("--contiguous", action="store_true")
    parser.add_argument("--job-name", type=str, default=JOB_NAME)
    parser.add_argument("--job-script", type=str, default=JOB_SCRIPT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    parser.add_argument("--callback-module", type=str, default=None)
    args = parser.parse_args()
    core(**args.__dict__)
