#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_build_autoconf
import generate_build_hdf5
import generate_build_help2man
import generate_build_netcdf
import utils


# >>> config: start
AUTOCONF_VERSION: str = "2.72"
BRANCH: str = "main"
ENV: defs.ProgrammingEnvironment = "gnu"
COMPILER_VERSION: str = "13.2.0"
HDF5_VERSION: str = "1.14.4.2"
MPI: defs.MPI = "hpcx"
NETCDF_VERSION: str = "4.9.2"
PARTITION: defs.Partition = "gpu"
ROOT_DIR: str = defs.root_dir
# >>> config: end


def core(
    autoconf_version: str,
    branch: str,
    env: defs.ProgrammingEnvironment,
    compiler_version: str,
    hdf5_version: str,
    mpi: defs.MPI,
    netcdf_version: str,
    partition: defs.Partition,
    root_dir: str,
) -> str:
    with utils.batch_file(prefix="prepare_pmapl") as (f, fname):
        # clear environment
        utils.module_purge(force=True)

        # load relevant modules
        utils.load_env(env)
        env_id = utils.load_compiler(env, compiler_version)
        mpi_id = utils.load_mpi(mpi, env, compiler_version, partition)
        utils.module_load("boost", "cmake", "python3/3.11.8-01")
        if partition == "gpu":
            utils.module_load("nvidia/22.11", "cuda/11.6")

        # set path to custom build of external dependencies
        generate_build_help2man.setup(env, compiler_version, root_dir)
        generate_build_autoconf.setup(env, compiler_version, root_dir, autoconf_version)
        generate_build_hdf5.setup(
            autoconf_version, env, compiler_version, mpi, partition, root_dir, hdf5_version
        )
        generate_build_netcdf.setup(
            autoconf_version,
            env,
            compiler_version,
            hdf5_version,
            mpi,
            partition,
            root_dir,
            netcdf_version,
        )

        # set path to PMAP code
        pmapl_dir = os.path.join(defs.root_dir, "pmapl", branch)
        assert os.path.exists(pmapl_dir)
        utils.export_variable("PMAPL", pmapl_dir)
        pmapl_venv_dir = os.path.join(pmapl_dir, "venv", partition, env_id, mpi_id)
        utils.export_variable("PMAPL_VENV", pmapl_venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(defs.root_dir, "pmapl", "gt_cache", env_id)
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # jump into project source directory and activate virtual environment (if it already exists)
        with utils.chdir(pmapl_dir, restore=False):
            if os.path.exists(pmapl_venv_dir):
                utils.run(f"source {pmapl_venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--autoconf-version", type=str, default=AUTOCONF_VERSION)
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--mpi", type=str, default=MPI)
    parser.add_argument("--netcdf-version", type=str, default=NETCDF_VERSION)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    args = parser.parse_args()
    core(**args.__dict__)
