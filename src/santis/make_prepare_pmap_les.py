#!/users/subbiali/spack/c4449cb201/opt/spack/linux-sles15-neoverse_v2/gcc-13.3.0/python-3.12.9-t554gwycoz72hebgyyp6am6btc6pfa4m/bin/python3.12
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import common
import defs
import utils


# >>> config: start
BRANCH: str = "unified-interface"
PYTHON_VERSION: defs.PythonVersion = "3.11"
# >>> config: end


def core(branch: str, python_version: defs.PythonVersion) -> str:
    with common.utils.batch_file(filename="prepare_ecrad") as (_, fname):
        # load spack env
        utils.spack_activate_ecrad_env(python_version)
        common.utils_spack.spack_load("boost")
        common.utils_spack.spack_load("cmake")
        common.utils_spack.spack_load("gcc")
        common.utils_spack.spack_load("hdf5")
        common.utils_spack.spack_load("netcdf-c")
        common.utils_spack.spack_load("netcdf-fortran")
        # common.utils_spack.spack_load(f"python@{python_version}")
        # py = utils.load_python(python_version)

        # set path to ecrad code
        pwd = os.path.abspath(os.environ.get("SCRATCH", os.path.curdir))
        ecrad_dir = os.path.join(pwd, "ecrad", branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)

        # add netcdf libs to linker and loader path
        common.utils.run("netcdfc_root=$(spack location -i netcdf-c)")
        common.utils.run("netcdff_root=$(spack location -i netcdf-fortran)")
        common.utils.export_variable("LDFLAGS", "-L${netcdfc_root}/lib")
        common.utils.export_variable(
            "LD_LIBRARY_PATH",
            "${netcdfc_root}/lib:${netcdff_root}/lib:$LD_LIBRARY_PATH",
        )

        with common.utils.chdir(ecrad_dir, restore=False):
            pass

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--python-version", type=str, default=PYTHON_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
