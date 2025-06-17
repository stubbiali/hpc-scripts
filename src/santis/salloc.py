#!/users/subbiali/spack/c4449cb201/opt/spack/linux-sles15-neoverse_v2/gcc-13.3.0/python-3.12.9-t554gwycoz72hebgyyp6am6btc6pfa4m/bin/python3.12
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import common
import defs


# >>> config: start
ACCOUNT: defs.Account = "c46"
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 4
PARTITION: defs.Partition = "normal"
TIME: str = "02:00:00"
# >>> config: end


def core(
    account: str, num_nodes: int, num_tasks_per_node: int, partition: defs.Partition, time: str
) -> None:
    command = [
        f"salloc",
        f"--account={account}",
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        f"--partition={partition}",
        f"--time={time}",
    ]
    common.utils.run(*command, verbose=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an allocation on the compute nodes.")
    parser.add_argument("--account", type=str, default=ACCOUNT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    args = parser.parse_args()
    core(**args.__dict__)
