#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
import argparse

import defs
import utils


# >>> config: start
ACCOUNT: int = 465000527
NUM_NODES: int = 1
NUM_TASKS_PER_NODE: int = 8
PARTITION_TYPE: defs.PartitionType = "gpu"
TIME: str = "01:00:00"
# >>> config: end


def core(
    account: int,
    num_nodes: int,
    num_tasks_per_node: int,
    partition_type: defs.PartitionType,
    time: str,
) -> None:
    partition = utils.get_partition(partition_type)
    command = [
        f"salloc",
        f"--account=project_{account}",
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        f"--partition={partition}",
        f"--time={time}",
    ]
    if partition_type == "gpu":
        command.append("--gpus-per-node=8")
    utils.run(*command, verbose=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an allocation on the compute nodes.")
    parser.add_argument("--account", type=int, default=ACCOUNT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--time", type=str, default=TIME)
    args = parser.parse_args()
    core(**args.__dict__)
