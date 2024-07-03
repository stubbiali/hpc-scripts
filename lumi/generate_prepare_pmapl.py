#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import defs
import generate_prepare_mpi
import utils


# >>> config: start
BRANCH: str = "coupling-refactoring"
COMPILER_VERSION: str = "16.0.1"
ENV: defs.ProgrammingEnvironment = "cray"
ENV_VERSION: str = "8.4.0"
HDF5_VERSION: str = "1.14.4.3"
NETCDF_VERSION: str = "4.9.2"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
STACK_VERSION: Optional[str] = "23.09"
# >>> config: end


def core(
    branch: str,
    compiler_version: str,
    env: defs.ProgrammingEnvironment,
    env_version: str,
    hdf5_version: str,
    netcdf_version: str,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
) -> tuple[str, str]:
    with utils.batch_file(prefix="prepare_pmapl") as (f, fname):
        # clear environment
        utils.module_reset()

        # load relevant modules
        utils.load_stack(stack, stack_version)
        utils.load_partition(partition_type)
        env, cpe = utils.load_env(env, env_version, partition_type, stack_version)
        compiler = utils.load_compiler(env, compiler_version)
        utils.module_load("Boost", "buildtools", "cray-python")
        if partition_type == "gpu":
            utils.module_load("rocm")

        # patch PYTHONPATH
        utils.export_variable("PYTHONPATH", "/opt/cray/pe/python/3.9.13.1")

        # set path to PMAP code
        pwd = os.path.abspath(os.environ.get("PROJECT", os.path.curdir))
        pmapl_dir = os.path.join(pwd, "pmapl", branch)
        assert os.path.exists(pmapl_dir)
        utils.export_variable("PMAPL", pmapl_dir)
        subtree = os.path.join(
            stack + "-" + stack_version or "", env + "-" + env_version, compiler.replace("/", "-")
        )
        pmapl_venv_dir = os.path.join(pmapl_dir, "venv", subtree)
        utils.export_variable("PMAPL_VENV", pmapl_venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(pmapl_dir, "gt_cache", subtree)
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip()

        # configure MPICH
        prepare_mpi_fname = generate_prepare_mpi.core(partition_type)
        utils.run(f". {prepare_mpi_fname}")

        # path to custom build of HDF5 and NetCDF-C
        utils.export_variable(
            "HDF5_ROOT", os.path.join(pwd, "hdf5", hdf5_version, "build", subtree)
        )
        utils.export_variable("HDF5_DIR", os.path.join(pwd, "hdf5", hdf5_version, "build", subtree))
        utils.export_variable(
            "NETCDF_ROOT", os.path.join(pwd, "netcdf-c", netcdf_version, "build", subtree)
        )
        utils.export_variable(
            "NETCDF4_DIR", os.path.join(pwd, "netcdf-c", netcdf_version, "build", subtree)
        )

        # jump into project source directory and activate virtual environment (if it already exists)
        with utils.chdir(pmapl_dir, restore=False):
            if os.path.exists(pmapl_venv_dir):
                utils.run(f"source {pmapl_venv_dir}/bin/activate")

    return fname, compiler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--env-version", type=str, default=ENV_VERSION)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=NETCDF_VERSION)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
