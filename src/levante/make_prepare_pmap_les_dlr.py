#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import defaults
from make_prepare_pmap_les import core


# >>> config: start
BRANCH: str = "main"
NUM_NODES: int = 1
# >>> config: end


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler", type=str, default=defaults.COMPILER)
    parser.add_argument(
        "--ghex-transport-backend", type=str, default=defaults.GHEX_TRANSPORT_BACKEND
    )
    parser.add_argument("--mpi", type=str, default=defaults.MPI)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--python", type=str, default=defaults.PYTHON)
    args = parser.parse_args()
    core(**args.__dict__, project_name="pmap-les-dlr")
