#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

from hpc_scripts import common
from hpc_scripts.lumi import (
    defaults,
    defs,
    make_build_hdf5,
    make_build_nco,
    make_build_netcdf,
    utils,
)

if TYPE_CHECKING:
    from typing import Optional


# >>> config: start
BRANCH: str = "cy49r1s-pmap"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    hdf5_version: str,
    nco_version: str,
    netcdf_version: str,
    partition: defs.Partition,
    rocm_version: str,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
) -> str:
    with common.utils.batch_file(filename="prepare_ecrad_porting") as (_, fname):
        # clear environment and load relevant modules
        cpe = utils.setup_env(env, partition, stack, stack_version, load_cdo=True)
        common.utils_module.module_load("buildtools", "cray-python")
        utils.load_boost(cpe, stack_version)
        partition_type = utils.get_partition_type(partition)
        if partition_type == "gpu":
            common.utils_module.module_load(f"rocm/{rocm_version}")

        # set path to ecrad-porting code
        ecrad_dir = os.path.join(common.config.ROOT_DIR, "ecrad-porting", branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)
        subtree = utils.get_subtree(env, stack, stack_version)
        venv_dir = os.path.join(ecrad_dir, "_venv", subtree)
        common.utils.export_variable("ECRAD_VENV", venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        # gt_cache_root = os.path.join(pwd, "ecrad-porting", "_gtcache", subtree)
        # common.utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        # common.utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        # common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip(rocm_version)

        # path to custom build of HDF5, NetCDF-C and NCO
        # note: NCO provides the utility ncks used in scripts/setup_optical_data.sh
        make_build_hdf5.setup(env, stack, stack_version, hdf5_version)
        make_build_netcdf.setup(env, stack, stack_version, hdf5_version, netcdf_version)
        make_build_nco.setup(env, stack, stack_version, hdf5_version, netcdf_version, nco_version)

        # jump into project source directory
        with common.utils.chdir(ecrad_dir, restore=False):
            if not os.path.exists(venv_dir):
                # create virtual environment if it does not exist yet
                common.utils.run(f"uv venv --prompt={subtree} {venv_dir}")
                common.utils.run(f"source {venv_dir}/bin/activate")
                common.utils.run("uv pip install -e .[dev,gpu,test]")
            else:
                # activate virtual environment
                common.utils.run(f"source {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--nco-version", type=str, default=defaults.NCO_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=defaults.NETCDF_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--rocm-version", type=str, default=defaults.ROCM_VERSION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
