#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import importlib
import os
from typing import TYPE_CHECKING

import common.utils
import defaults

if TYPE_CHECKING:
    from typing import Callable, Optional

    import defs


# >>> config: start
CONTIGUOUS_NODES: bool = False
DRY_RUN: bool = False
JOB_NAME: str = "test_job"
JOB_SCRIPT: str = "test_job"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 1
RESERVATION: Optional[str] = None
SET_SWITCHES: bool = False
TIME: str = "01:00:00"
# >>> config: end


def core(
    account: str,
    contiguous_nodes: bool,
    dry_run: bool,
    job_name: str,
    job_script: str,
    num_nodes: int,
    num_tasks_per_node: int,
    partition: defs.Partition,
    reservation: Optional[str],
    set_switches: bool,
    time: str,
    *,
    callback_module: Optional[str] = None,
) -> None:
    if callback_module is not None:
        mod = importlib.import_module(callback_module)
        cb: Callable[[], str] = getattr(mod, "callback", None)
        assert cb is not None, f"Module `{callback_module}` must define `callback()`."
        job_script = cb()

    with common.utils.batch_directory() as job_dir:
        error = os.path.join(job_dir, "error.txt")
        output = os.path.join(job_dir, "output.txt")
        with common.utils.batch_file(filename="batch") as (_, batch_file):
            command = [
                "sbatch",
                f"--account={account}",
                f"--constraint={partition}",
                f"--distribution=block",
                f"--error={error}",
                f"--exclusive",
                f"--export=ALL",
                f"--job-name={job_name}",
                f"--nodes={num_nodes}",
                f"--ntasks-per-node={num_tasks_per_node}",
                f"--output={output}",
                f"--partition={'large' if num_nodes > 2400 else 'normal'}",
                f"--time={time}",
            ]
            if reservation:
                command.append(f"--reservation={reservation}")
            if contiguous_nodes and num_nodes <= 256:
                # we ask for contiguous nodes only when the number of nodes does not exceed 256
                # the request of a larger number of contiguous nodes might not be satisfied by the
                # scheduler, due to the presence of faulty nodes
                command.append(f"--contiguous")
            if set_switches:
                command.append(f"--switches={1 + (num_nodes - 1) // 384}")
                # command.append(f"--switches={num_switches}@12:00:00")
            command.append(job_script)
            common.utils.run(*command, split=True)

    if not dry_run:
        common.utils.run(f". {batch_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit a batch job.")
    parser.add_argument("--account", type=str, default=defaults.ACCOUNT)
    parser.add_argument("--contiguous-nodes", type=bool, default=CONTIGUOUS_NODES)
    parser.add_argument("--dry-run", type=bool, default=DRY_RUN)
    parser.add_argument("--job-name", type=str, default=JOB_NAME)
    parser.add_argument("--job-script", type=str, default=JOB_SCRIPT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--set-switches", type=bool, default=SET_SWITCHES)
    parser.add_argument("--time", type=str, default=TIME)
    parser.add_argument("--callback-module", type=str, default=None)
    args = parser.parse_args()
    core(**args.__dict__)
