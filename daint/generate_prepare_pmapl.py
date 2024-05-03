#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_prepare_mpi
import utils


# >>> config: start
BRANCH: str = "cloudsc-cy49r1"
ENV: defs.ProgrammingEnvironment = "gnu"
PARTITION: defs.Partition = "gpu"
# >>> config: end


def core(branch: str, env: defs.ProgrammingEnvironment, partition: defs.Partition) -> str:
    with utils.batch_file(prefix="prepare_pmapl") as (f, fname):
        # clear environment
        utils.module_purge(force=True)

        # load relevant modules
        utils.load_partition(partition)
        utils.load_env(env)
        utils.module_load("Boost", "cray-mpich", "cray-python", "CMake")
        if partition == "gpu":
            utils.module_load("cudatoolkit/11.2.0_3.39-2.1__gf93aa1c")

        # set path to PMAP code
        pwd = os.environ.get("SCRATCH", os.path.curdir)
        pmapl_dir = os.path.join(pwd, "pmapl", branch)
        assert os.path.exists(pmapl_dir)
        utils.export_variable("PMAPL", pmapl_dir)
        pmapl_venv_dir = os.path.join(pmapl_dir, "venv", env)
        utils.export_variable("PMAPL_VENV", pmapl_venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        # gt_cache_root = os.path.join(pmapl_dir, "gt_cache", env)
        gt_cache_root = os.path.join(pwd, "pmapl", "gt_cache", env)
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # configure MPICH
        prepare_mpi_fname = generate_prepare_mpi.core(partition)
        utils.run(f". {prepare_mpi_fname}")

        # set/fix CUDA-related variables
        if partition == "gpu":
            utils.setup_cuda()

        # path to custom build of HDF5 and NetCDF-C
        home_dir = os.environ.get("HOME", f"/users/{os.getlogin()}")
        utils.export_variable("HDF5_ROOT", os.path.join(home_dir, f"hdf5/1.14.2/build/{env}"))
        utils.export_variable("HDF5_DIR", os.path.join(home_dir, f"hdf5/1.14.2/build/{env}"))
        utils.export_variable("NETCDF_ROOT", os.path.join(home_dir, f"netcdf-c/4.9.2/build/{env}"))
        utils.export_variable("NETCDF4_DIR", os.path.join(home_dir, f"netcdf-c/4.9.2/build/{env}"))

        # jump into project source directory and activate virtual environment (if it already exists)
        with utils.chdir(pmapl_dir, restore=False):
            if os.path.exists(pmapl_venv_dir):
                utils.run(f"source {pmapl_venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
