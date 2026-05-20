#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

from hpc_scripts import common
from hpc_scripts.lumi import defaults, defs, make_build_hdf5, make_build_netcdf, utils

if TYPE_CHECKING:
    from typing import Optional


# >>> config: start
BRANCH: str = "master"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    hdf5_version: str,
    netcdf_version: str,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
) -> str:
    with common.utils.batch_file(filename="prepare_ecrad") as (_, fname):
        # clear environment and load relevant modules
        cpe = utils.setup_env(env, partition, stack, stack_version, load_cdo=True)
        common.utils_module.module_load("buildtools", "cray-python")
        utils.load_boost(cpe, stack_version)

        # set path to ecrad code
        ecrad_dir = os.path.join(common.config.ROOT_DIR, "ecrad", branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)

        # setup custom build of HDF5 and NetCDF-C
        make_build_hdf5.setup(env, stack, stack_version, hdf5_version)
        make_build_netcdf.setup(env, stack, stack_version, hdf5_version, netcdf_version)

        # jump into project source directory
        with common.utils.chdir(ecrad_dir, restore=False):
            pass

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=defaults.NETCDF_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
