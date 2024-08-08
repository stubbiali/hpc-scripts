#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
import argparse

import defs
import utils


# >>> config: start

# project_id="$(sacct --format=Account --noheader | head -n 1 | awk '{$1=$1}1')"
# ACCOUNT: str = project_id
ACCOUNT: str = "s299"
NUM_NODES: int = 1
PARTITION: defs.Partition = "gpu"
TIME: str = "01:00:00"
# >>> config: end

def core(account: int, num_nodes: int, partition: defs.Partition, time: str) -> None:
    command = [
        f"salloc",
        f"--account={account}{'m' if partition == 'mc' else ''}",
        f"--constraint={partition}",
        f"--nodes={num_nodes}",
        f"--partition=normal",
        f"--time={time}",
    ]
    utils.run(*command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an allocation on the compute nodes.")
    parser.add_argument("--account", type=str, default=ACCOUNT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    args = parser.parse_args()
    core(**args.__dict__)
