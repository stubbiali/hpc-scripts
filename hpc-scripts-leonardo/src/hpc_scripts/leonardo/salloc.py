#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from typing import Optional

from hpc_scripts import common
from hpc_scripts.leonardo import defaults, defs, utils

# >>> config: start
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 4
# >>> config: end


def core(
    account: str,
    num_nodes: int,
    num_tasks_per_node: int,
    partition: defs.Partition,
    qos: defs.QOS,
    time: Optional[str],
) -> None:
    time = utils.check_slurm_settings(partition, qos, num_nodes, time)
    common.utils.run(
        "salloc",
        f"--account={account}",
        "--exclusive",
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        f"--partition={partition}",
        f"--qos={qos}",
        f"--time={time}",
        verbose=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Get an allocation on the compute nodes.")
    parser.add_argument("--account", type=str, default=defaults.ACCOUNT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--qos", type=str, default=defaults.QOS[defaults.PARTITION])
    parser.add_argument("--time", type=str, default=None)
    args = parser.parse_args()
    core(**args.__dict__)


if __name__ == "__main__":
    main()
