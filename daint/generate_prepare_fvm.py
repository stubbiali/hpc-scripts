#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_prepare_mpi
import utils


# >>> config: start
BRANCH: str = "upgrade-ghex"
ENV: defs.ProgrammingEnvironment = "gnu"
PARTITION: defs.Partition = "gpu"
# >>> config: end


def core(branch: str, env: defs.ProgrammingEnvironment, partition: defs.Partition) -> str:
    with utils.batch_file(prefix="prepare_fvm") as (f, fname):
        # clear environment
        utils.module_purge(force=True)

        # load relevant modules
        utils.load_partition(partition)
        utils.load_env(env)
        utils.module_load("Boost", "cray-mpich", "cray-python", "CMake")
        if partition == "gpu":
            utils.module_load("cudatoolkit/11.2.0_3.39-2.1__gf93aa1c")

        # set path to FVM code
        pwd = os.environ.get("SCRATCH", os.path.curdir)
        gt4py_dir = os.path.join(pwd, "fvm-gt4py", branch)
        assert os.path.exists(gt4py_dir)
        utils.export_variable("FVM", gt4py_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(pwd, "fvm-gt4py", branch, "gt_cache", env)
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
        home_dir = os.environ.get("HOME", "/users/subbiali")
        utils.export_variable("HDF5_ROOT", os.path.join(home_dir, f"hdf5/1.14.2/build/{env}"))
        utils.export_variable("NETCDF_ROOT", os.path.join(home_dir, f"netcdf-c/4.9.2/build/{env}"))

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    args = parser.parse_args()
    core(**args.__dict__)
