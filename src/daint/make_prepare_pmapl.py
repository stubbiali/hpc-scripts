#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

import common.utils
import common.utils_module
import defaults
import make_prepare_mpi
import utils

if TYPE_CHECKING:
    from typing import Optional

    import defs


# >>> config: start
BRANCH: str = "benchmarking"
ROOT_DIR: Optional[str] = None
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    ghex_transport_backend: defs.GHEXTransportBackend,
    partition: defs.Partition,
    root_dir: Optional[str],
) -> tuple[str, str]:
    with common.utils.batch_file(filename="prepare_pmapl") as (f, fname):
        # load relevant modules
        utils.setup_env(env, partition)
        common.utils_module.module_load("Boost", "cray-mpich", "cray-python", "CMake")
        if partition == "gpu":
            common.utils_module.module_load("cudatoolkit/11.2.0_3.39-2.1__gf93aa1c")

        # set path to PMAP code
        root_dir = os.path.abspath(root_dir or os.path.curdir)
        pmapl_dir = os.path.join(root_dir, "pmapl", branch)
        assert os.path.exists(pmapl_dir)
        common.utils.export_variable("PMAPL", pmapl_dir)
        pmapl_venv_dir = os.path.join(
            pmapl_dir,
            (
                "_venv"
                + (
                    f"_{ghex_transport_backend}"
                    if ghex_transport_backend in ("libfabric", "ucx")
                    else ""
                )
                + "_cpu"
                if partition == "mc"
                else ""
            ),
            env,
        )
        common.utils.export_variable("PMAPL_VENV", pmapl_venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(
            root_dir, "pmapl", "_gtcache" + "_cpu" if partition == "mc" else "", env
        )
        common.utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        common.utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # configure MPICH
        prepare_mpi_fname = make_prepare_mpi.core(partition)
        common.utils.run(f". {prepare_mpi_fname}")

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
        with common.utils.chdir(pmapl_dir, restore=False):
            if os.path.exists(pmapl_venv_dir):
                common.utils.run(f"source {pmapl_venv_dir}/bin/activate")

    return fname, gt_cache_root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument(
        "--ghex-transport-backend", type=str, default=defaults.GHEX_TRANSPORT_BACKEND
    )
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    args = parser.parse_args()
    core(**args.__dict__)
