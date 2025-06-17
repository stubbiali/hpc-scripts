#!/users/subbiali/spack/c4449cb201/opt/spack/linux-sles15-neoverse_v2/gcc-13.3.0/python-3.12.9-t554gwycoz72hebgyyp6am6btc6pfa4m/bin/python3.12
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import importlib
import os
from typing import TYPE_CHECKING

import common.utils
import defs

if TYPE_CHECKING:
    from typing import Callable, Optional


# >>> config: start
ACCOUNT: str = "c46"
DRY_RUN: bool = False
JOB_NAME: str = "test_job"
JOB_SCRIPT: str = "test_job"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 4
PARTITION: defs.Partition = "normal"
TIME: str = "01:00:00"
# >>> config: end


def core(
    account: defs.Account,
    dry_run: bool,
    job_name: str,
    job_script: str,
    num_nodes: int,
    num_tasks_per_node: int,
    partition: defs.Partition,
    time: str,
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
            command = (
                "sbatch",
                f"--account={account}",
                f"--error={error}",
                f"--export=ALL",
                f"--job-name={job_name}",
                f"--nodes={num_nodes}",
                f"--ntasks-per-node={num_tasks_per_node}",
                f"--output={output}",
                f"--partition={partition}",
                f"--time={time}",
                job_script,
            )
            common.utils.run(*command, split=True)

    if not dry_run:
        common.utils.run(f". {batch_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submit a batch job.")
    parser.add_argument("--account", type=int, default=ACCOUNT)
    parser.add_argument("--job-name", type=str, default=JOB_NAME)
    parser.add_argument("--job-script", type=str, default=JOB_SCRIPT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    parser.add_argument("--callback-module", type=str, default=None)
    args = parser.parse_args()
    core(**args.__dict__)
