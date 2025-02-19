#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

import common.utils
import common.utils_module
import defaults
import utils

if TYPE_CHECKING:
    from typing import Optional

    import defs


# >>> config: start
BRANCH: str = "_tests"
ROOT_DIR: Optional[str] = None
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    root_dir: Optional[str],
) -> tuple[str, str]:
    with common.utils.batch_file(filename="prepare_ecrad") as (f, fname):
        # load relevant modules
        utils.setup_env(env, partition)
        common.utils_module.module_load("Boost", "cray-python", "CMake")
        if partition == "gpu":
            common.utils_module.module_load("cudatoolkit/11.2.0_3.39-2.1__gf93aa1c")

        # set path to PMAP code
        root_dir = os.path.abspath(root_dir or os.path.curdir)
        ecrad_dir = os.path.join(root_dir, "ecrad", branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)

        # set/fix CUDA-related variables
        if partition == "gpu":
            utils.setup_cuda()

        # jump into project source directory
        with common.utils.chdir(ecrad_dir, restore=False):
            pass

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    args = parser.parse_args()
    core(**args.__dict__)
