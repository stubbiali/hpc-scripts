#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import stat

from hpc_scripts import common


def core() -> str:
    with common.utils.output_file(filename="select_gpu") as (_, fname):
        common.utils.run("export CUDA_VISIBLE_DEVICES=$SLURM_LOCALID")
        common.utils.run("export UCX_NET_DEVICES=mlx5_$SLURM_LOCALID:1")
        common.utils.run("exec $*")
    os.chmod(fname, stat.S_IRWXU)
    return fname


def main() -> None:
    core()


if __name__ == "__main__":
    main()
