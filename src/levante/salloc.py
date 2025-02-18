#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import TYPE_CHECKING

import common.utils
import defaults
import utils_slurm

if TYPE_CHECKING:
    import defs


# >>> config: start
NUM_NODES: int = 1
TIME: str = "01:00:00"
# >>> config: end


def core(account: str, num_nodes: int, partition: defs.Partition, time: str) -> None:
    command = [
        f"salloc",
        f"--account={account}{'_gpu' if partition == 'gpu' else ''}",
        f"--nodes={num_nodes}",
        f"--partition={partition}",
        f"--qos=normal",
        f"--time={time}",
        *utils_slurm.get_slurm_options(partition),
    ]
    common.utils.run(*command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an allocation on the compute nodes.")
    parser.add_argument("--account", type=str, default=defaults.ACCOUNT)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--time", type=str, default=TIME)
    args = parser.parse_args()
    core(**args.__dict__)
