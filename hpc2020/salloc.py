#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os

import defs
import utils


# >>> config: start

ACCOUNT: str = os.environ.get("ECACCOUNT", "")
NUM_NODES: int = 1
PARTITION: defs.Partition = "gpu"
TIME: str = "01:00:00"
# >>> config: end


def core(account: int, num_nodes: int, partition: defs.Partition, time: str) -> None:
    command = [
        f"salloc",
        f"--account={account}",
        f"--nodes={num_nodes}",
        f"--partition={partition}",
        f"--time={time}",
    ]
    command += ["--qos=ng", "--gpus=1"] if partition == "gpu" else ["--qos=np"]
    utils.run(*command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an allocation on the compute nodes.")
    parser.add_argument("--account", type=str, default=ACCOUNT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    args = parser.parse_args()
    core(**args.__dict__)
