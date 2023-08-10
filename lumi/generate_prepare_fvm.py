#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils


# >>> config: start
BRANCH: str = "main"
ENV: defs.ProgrammingEnvironment = "cray"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
) -> str:
    with utils.batch_file(prefix="prepare_fvm") as (f, fname):
        # clear environment
        utils.module_purge(force=True)

        # load relevant modules
        utils.load_stack(stack)
        suffix = utils.load_partition(partition_type)
        cpe = utils.load_env(env)
        utils.module_load(f"Boost/1.79.0-{cpe}-22.08", "buildtools", "cray-python")
        if partition_type == "gpu":
            utils.module_load("rocm")

        # patch PYTHONPATH
        utils.export_variable("PYTHONPATH", "/opt/cray/pe/python/3.9.12.1")

        # set path to FVM code
        pwd = os.environ.get("PROJECT", os.path.curdir)
        gt4py_dir = os.path.join(pwd, "fvm-gt4py", branch)
        assert os.path.exists(gt4py_dir)
        utils.export_variable("FVM", gt4py_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(pwd, "fvm-gt4py", "gt_cache", f"{env}{suffix}")
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))
        utils.export_variable("GHEX_BUILD_PREFIX", f"{env}{suffix}")

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip()

        # path to custom build of HDF5 and NetCDF-C
        utils.export_variable("HDF5_ROOT", os.path.join(pwd, f"hdf5/1.14.1-2/build/{env}{suffix}"))
        utils.export_variable(
            "NETCDF_ROOT", os.path.join(pwd, f"netcdf-c/4.9.2/build/{env}{suffix}")
        )

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    args = parser.parse_args()
    core(**args.__dict__)
