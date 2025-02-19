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
    import defs


# >>> config: start
BRANCH: str = "v0.1.0"
# >>> config: end


def core(branch: str, env: defs.ProgrammingEnvironment, partition: defs.Partition) -> str:
    with common.utils.batch_file(filename="prepare_taz") as (f, fname):
        # clear environment
        common.utils_module.module_purge(force=True)

        # load relevant modules
        utils.load_partition(partition)
        utils.load_env(env)
        common.utils_module.module_load("Boost", "CMake", "cray-hdf5", "cray-netcdf", "cray-python")
        if partition == "gpu":
            common.utils_module.module_load("cudatoolkit/11.2.0_3.39-2.1__gf93aa1c")

        # set path to the source code of the project
        pwd = os.path.abspath(os.environ.get("SCRATCH", os.path.curdir))
        project_dir = os.path.join(pwd, "tasmania", branch)
        assert os.path.exists(project_dir)
        common.utils.export_variable("TAZ", project_dir)
        venv_dir = os.path.join(project_dir, "venv", env)
        common.utils.export_variable("TAZ_VENV", venv_dir)

        # low-level GT4Py and DaCe
        gt_cache_root = os.path.join(project_dir, "gt_cache", env)
        common.utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        common.utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix CUDA-related variables
        if partition == "gpu":
            utils.setup_cuda()

        # jump into project root directory and activate virtual environment (if it already exists)
        with common.utils.chdir(project_dir, restore=False):
            if os.path.exists(venv_dir):
                common.utils.run(f". {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
