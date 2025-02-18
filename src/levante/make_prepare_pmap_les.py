#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

import common.utils
import common.utils_module
import common.utils_spack
import defaults
import utils_module
import utils_mpi
import utils_spack

if TYPE_CHECKING:
    import defs


# >>> config: start
BRANCH: str = "main"
NUM_NODES: int = 1
# >>> config: end


def core(
    branch: str,
    compiler: defs.Compiler,
    mpi: defs.MPI,
    num_nodes: int,
    partition: defs.Partition,
    python: defs.Python,
    project_name: str = "pmap-les",
) -> str:
    project_name_with_underscores = project_name.replace("-", "_")
    with common.utils.batch_file(filename=f"prepare_{project_name_with_underscores}") as (f, fname):
        # clear environment
        common.utils_module.module_purge(force=True)
        common.utils_spack.spack_unload()

        # load compilers
        utils_module.module_load_compiler(compiler)
        utils_mpi.load_mpi(compiler, mpi, partition, num_nodes)

        # load relevant modules
        # utils.module_load(f"netcdf-c/4.8.1-{mpi_id}")
        # utils.module_load("python3/2023.01-gcc-11.2.0")
        # if partition == "gpu":
        #     utils.module_load(f"nvhpc/23.9-{compiler_id}")

        # load relevant spack packages
        common.utils_spack.spack_load("boost@1.85.0", compiler="gcc@11.2.0")
        common.utils_spack.spack_load("cmake@3.30.2", compiler="gcc@11.2.0")
        common.utils_spack.spack_load("git@2.43.3", compiler="gcc@11.2.0")
        common.utils_spack.spack_load("neovim@0.10.0", compiler="gcc@11.2.0")
        utils_spack.spack_load_netcdf(compiler, mpi)
        utils_spack.spack_load_python(python)
        if partition == "gpu":
            cuda_version = utils_spack.spack_load_cuda(compiler, mpi)

        # set path to PMAP code
        pwd = os.environ.get("WORK", os.path.curdir)
        project_dir = os.path.join(pwd, project_name, branch)
        assert os.path.exists(project_dir)
        env_var_prefix = project_name_with_underscores.upper()
        common.utils.export_variable(env_var_prefix, project_dir)
        venv_hash = python + "-" + compiler + "-" + mpi
        if partition != "gpu":
            venv_hash += "-cpu"
        venv_dir = os.path.join(project_dir, "_venv", venv_hash)
        common.utils.export_variable(f"{env_var_prefix}_VENV", venv_dir)

        # low-level GT4Py, DaCe and GHEX config
        gt_cache_root = os.path.join(pwd, project_name, "_gtcache", venv_hash)
        common.utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        common.utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))
        common.utils.export_variable("GHEX_TRANSPORT_BACKEND", "UCX")
        if partition == "gpu":
            common.utils.export_variable("GHEX_USE_GPU", "True")
            common.utils.export_variable("GHEX_GPU_TYPE", "NVIDIA")
            common.utils.export_variable("GHEX_GPU_ARCH", "80")
        else:
            common.utils.export_variable("GHEX_USE_GPU", "False")

        # jump into project source directory, create virtual environment (if it does not exist yet)
        #  and activate it
        with common.utils.chdir(project_dir, restore=False):
            if not os.path.exists(venv_dir):
                common.utils.run(f"python -m venv {venv_dir}")
                common.utils.run(f". {venv_dir}/bin/activate")
                common.utils.run("pip install --upgrade pip setuptools wheel")
                # optional_dependencies = "mpi"
                optional_dependencies = "dev,mpi-test"
                if partition == "gpu":
                    optional_dependencies += f",gpu-cuda{cuda_version}x"
                common.utils.run(f"pip install -e .[{optional_dependencies}] --no-cache-dir")
            else:
                common.utils.run(f". {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler", type=str, default=defaults.COMPILER)
    parser.add_argument("--mpi", type=str, default=defaults.MPI)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--python", type=str, default=defaults.PYTHON)
    args = parser.parse_args()
    core(**args.__dict__)
