#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import stat

from hpc_scripts import common


def core() -> str:
    with common.utils.batch_file(filename="select_gpu") as (_, fname):
        common.utils.run("export ROCR_VISIBLE_DEVICES=$SLURM_LOCALID")
        common.utils.run("exec $*")
    os.chmod(fname, stat.S_IRWXU)
    return fname


def main() -> None:
    core()


if __name__ == "__main__":
    main()
