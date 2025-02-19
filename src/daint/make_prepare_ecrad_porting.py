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
BRANCH: str = "refactor"
ROOT_DIR: Optional[str] = None
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    root_dir: Optional[str],
) -> tuple[str, str]:
    with common.utils.batch_file(filename="prepare_ecrad_porting") as (f, fname):
        # load relevant modules
        utils.setup_env(env, partition)
        common.utils_module.module_load("Boost", "CDO", "CMake", "cray-python")
        if partition == "gpu":
            common.utils_module.module_load("cudatoolkit/11.2.0_3.39-2.1__gf93aa1c")

        # set path to ecrad_porting code
        root_dir = os.path.abspath(root_dir or os.path.curdir)
        ecrad_dir = os.path.join(root_dir, "ecrad-porting", branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)
        ecrad_venv_dir = os.path.join(
            ecrad_dir, "_venv" + ("_cpu" if partition == "mc" else ""), env
        )
        common.utils.export_variable("ECRAD_VENV", ecrad_venv_dir)

        # configure fmodpy, gt4py and dace cache
        cache_root = os.path.join(
            root_dir, "ecrad-porting", "_cache" + ("_cpu" if partition == "mc" else "")
        )
        common.utils.export_variable("FMODPY_CACHE_ROOT", cache_root)
        common.utils.export_variable("GT_CACHE_ROOT", cache_root)
        common.utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        common.utils.export_variable("DACE_CONFIG", os.path.join(cache_root, ".dace.conf"))

        # set/fix CUDA-related variables
        if partition == "gpu":
            utils.setup_cuda()

        # path to custom build of HDF5 and NetCDF-C
        home_dir = os.environ.get("HOME", f"/users/{os.getlogin()}")
        common.utils.export_variable(
            "HDF5_ROOT", os.path.join(home_dir, f"hdf5/1.14.4.2/build/{env}")
        )
        common.utils.export_variable(
            "HDF5_DIR", os.path.join(home_dir, f"hdf5/1.14.4.2/build/{env}")
        )
        common.utils.export_variable(
            "NETCDF_ROOT", os.path.join(home_dir, f"netcdf-c/4.9.2/build/{env}")
        )
        common.utils.export_variable(
            "NETCDF4_DIR", os.path.join(home_dir, f"netcdf-c/4.9.2/build/{env}")
        )

        # jump into project source directory and activate virtual environment (if it already exists)
        with common.utils.chdir(ecrad_dir, restore=False):
            if os.path.exists(ecrad_venv_dir):
                common.utils.run(f"source {ecrad_venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    args = parser.parse_args()
    core(**args.__dict__)
