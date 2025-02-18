# -*- coding: utf-8 -*-
from __future__ import annotations

import common.utils
import defs


def get_slurm_options(partition: defs.Partition) -> list[str]:
    options = ["--mem=0"]
    with common.utils.check_argument("partition", partition, defs.valid_partitions):
        if partition == "gpu":
            options.append("--constraint=a100_80")
            options.append("--gpus-per-node=4")
    return options
