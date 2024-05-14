#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils


# >>> config: start
BRANCH: str = "main"
ENV: defs.ProgrammingEnvironment = "gnu"
HDF5_VERSION: str = "1.14.4.2"
MPI: defs.MPI = "openmpi"
NETCDF_VERSION: str = "4.9.2"
PARTITION: defs.Partition = "gpu"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    hdf5_version: str,
    mpi: defs.MPI,
    netcdf_version: str,
    partition: defs.Partition,
) -> str:
    with utils.batch_file(prefix="prepare_pmapl") as (f, fname):
        # clear environment
        utils.module_purge(force=True)

        # load relevant modules
        utils.load_env(env)
        utils.load_mpi(env, mpi, partition)
        utils.module_load("boost", "cmake", "python3/3.11.8-01")
        if partition == "gpu":
            utils.module_load("nvidia/22.11", "cuda/11.6")
            # utils.setup_cuda()

        # set path to PMAP code
        pmapl_dir = os.path.join(defs.root_dir, "pmapl", branch)
        assert os.path.exists(pmapl_dir)
        utils.export_variable("PMAPL", pmapl_dir)
        pmapl_venv_dir = os.path.join(pmapl_dir, "venv", partition, env, mpi)
        utils.export_variable("PMAPL_VENV", pmapl_venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(defs.root_dir, "pmapl", "gt_cache", env)
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # path to custom build of HDF5 and NetCDF-C
        utils.export_variable(
            "HDF5_ROOT", os.path.join(defs.root_dir, f"hdf5/{hdf5_version}/build/{env}/{mpi}")
        )
        utils.export_variable(
            "HDF5_DIR", os.path.join(defs.root_dir, f"hdf5/{hdf5_version}/build/{env}/{mpi}")
        )
        utils.export_variable(
            "NETCDF_ROOT",
            os.path.join(defs.root_dir, f"netcdf-c/{netcdf_version}/build/{env}/{mpi}"),
        )
        utils.export_variable(
            "NETCDF4_DIR",
            os.path.join(defs.root_dir, f"netcdf-c/{netcdf_version}/build/{env}/{mpi}"),
        )

        # jump into project source directory and activate virtual environment (if it already exists)
        with utils.chdir(pmapl_dir, restore=False):
            if os.path.exists(pmapl_venv_dir):
                utils.run(f"source {pmapl_venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--mpi", type=str, default=MPI)
    parser.add_argument("--netcdf-version", type=str, default=NETCDF_VERSION)
    parser.add_argument("--partition", type=str, default=PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
