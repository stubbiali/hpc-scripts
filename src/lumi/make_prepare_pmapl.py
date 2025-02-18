#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import update_path  # noqa: F401

import common.utils as common_utils
import defaults
import defs
import make_prepare_mpi
import utils


# >>> config: start
BRANCH: str = "benchmarking-lumi"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    ghex_transport_backend: defs.GHEXTransportBackend,
    hdf5_version: str,
    netcdf_version: str,
    partition: defs.Partition,
    rocm_version: str,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
) -> tuple[str, str]:
    with common_utils.batch_file(filename="prepare_pmapl") as (f, fname):
        # clear environment and load relevant modules
        cpe = utils.setup_env(env, partition, stack, stack_version)
        common_utils.module_load(f"Boost/1.83.0-{cpe}", "buildtools", "cray-python")
        partition_type = utils.get_partition_type(partition)
        if partition_type == "gpu":
            common_utils.module_load(f"rocm/{rocm_version}")

        # set path to PMAP code
        pwd = os.path.abspath(os.environ.get("PROJECT", os.path.curdir))
        pmapl_dir = os.path.join(pwd, "pmapl", branch)
        assert os.path.exists(pmapl_dir)
        common_utils.export_variable("PMAPL", pmapl_dir)
        pmapl_subtree = utils.get_subtree(
            env,
            stack,
            stack_version,
            ghex_transport_backend=ghex_transport_backend,
            rocm_version=rocm_version if partition_type == "gpu" else None,
        )
        pmapl_venv_dir = os.path.join(pmapl_dir, "_venv", pmapl_subtree)
        common_utils.export_variable("PMAPL_VENV", pmapl_venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        subtree = utils.get_subtree(env, stack, stack_version)
        gt_cache_root = os.path.join(pwd, "pmapl", "_gtcache", subtree)
        common_utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        common_utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        common_utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip(rocm_version)

        # configure MPICH
        prepare_mpi_fname = make_prepare_mpi.core(ghex_transport_backend, partition)
        common_utils.run(f". {prepare_mpi_fname}")

        # path to custom build of HDF5 and NetCDF-C
        common_utils.export_variable(
            "HDF5_ROOT", os.path.join(pwd, "hdf5", hdf5_version, "build", subtree)
        )
        common_utils.export_variable(
            "HDF5_DIR", os.path.join(pwd, "hdf5", hdf5_version, "build", subtree)
        )
        common_utils.export_variable(
            "NETCDF_ROOT", os.path.join(pwd, "netcdf-c", netcdf_version, "build", subtree)
        )
        common_utils.export_variable(
            "NETCDF4_DIR", os.path.join(pwd, "netcdf-c", netcdf_version, "build", subtree)
        )

        # jump into project source directory
        with common_utils.chdir(pmapl_dir, restore=False):
            if not os.path.exists(pmapl_venv_dir):
                # create virtual environment if it does not exist yet
                common_utils.run(f"python -m venv --prompt={pmapl_subtree} {pmapl_venv_dir}")
                common_utils.run(f"source {pmapl_venv_dir}/bin/activate")
                common_utils.run(f"pip install --upgrade pip setuptools wheel")
                common_utils.run(
                    f"CC=cc CXX=CC MPICC=cc MPICXX=CC pip install -e .[mpi,gpu-rocm] --no-cache-dir"
                )
            else:
                # activate virtual environment
                common_utils.run(f"source {pmapl_venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument(
        "--ghex-transport-backend", type=str, default=defaults.GHEX_TRANSPORT_BACKEND
    )
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=defaults.NETCDF_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--rocm-version", type=str, default=defaults.ROCM_VERSION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
