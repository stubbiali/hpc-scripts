#!/users/subbiali/spack/c4449cb201/opt/spack/linux-sles15-neoverse_v2/gcc-13.3.0/python-3.12.9-t554gwycoz72hebgyyp6am6btc6pfa4m/bin/python3.12
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import common
import defs
import utils


# >>> config: start
BRANCH: str = "solvers-cy49r1"
PYTHON_VERSION: defs.PythonVersion = "3.11"
# >>> config: end


def core(branch: str, python_version: defs.PythonVersion) -> str:
    with common.utils.batch_file(filename="prepare_ecrad_porting") as (_, fname):
        # load spack env
        utils.spack_activate_ecrad_env(python_version)
        common.utils_spack.spack_load("boost")
        common.utils_spack.spack_load("cmake")
        common.utils_spack.spack_load("cuda")
        common.utils_spack.spack_load("gcc")
        common.utils_spack.spack_load("hdf5")
        common.utils_spack.spack_load("netcdf-c")
        common.utils_spack.spack_load(f"python@{python_version}")
        # py = utils.load_python(python_version)

        # set path to ecrad-porting code
        pwd = os.path.abspath(os.environ.get("SCRATCH", os.path.curdir))
        ecrad_dir = os.path.join(pwd, "ecrad-porting", branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)
        venv_dir = os.path.join(ecrad_dir, f"_venv/py{python_version.replace('.', '')}")
        common.utils.export_variable("ECRAD_VENV", venv_dir)

        # jump into project source directory
        with common.utils.chdir(ecrad_dir, restore=False):
            if not os.path.exists(venv_dir):
                # create virtual environment if it does not exist yet
                common.utils.run(f"python -m venv {venv_dir}")
                common.utils.run(f"source {venv_dir}/bin/activate")
                common.utils.run(f"pip install --upgrade pip setuptools wheel")
                common.utils.run(f"pip install -e .[dev,gpu-cuda12x,test] --no-cache-dir")
            else:
                # activate virtual environment
                common.utils.run(f"source {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--python-version", type=str, default=PYTHON_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
