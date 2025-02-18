#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import TYPE_CHECKING

import make_prepare_pmap_les

if TYPE_CHECKING:
    import defs


# >>> config: start
BRANCH: str = "main"
COMPILER: defs.Compiler = "nvhpc@24.7"
MPI: defs.MPI = "openmpi@4.1.5"
NUM_NODES: int = 1
PARTITION: defs.Partition = "gpu"
PYTHON: str = "python@3.11"
# >>> config: end


core = make_prepare_pmap_les.core


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler", type=str, default=COMPILER)
    parser.add_argument("--mpi", type=str, default=MPI)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--python", type=str, default=PYTHON)
    args = parser.parse_args()
    core(**args.__dict__, project_name="pmap-les-dlr")
