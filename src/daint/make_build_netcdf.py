#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

import common.utils
import common.utils_module
import defaults
import utils

if TYPE_CHECKING:
    import defs


# >>> config: start
HDF5_VERSION: str = "1.14.2"
ROOT_DIR: str = f"/users/{os.getlogin()}"
VERSION: str = "4.9.2"
# >>> config: end


def core(
    env: defs.ProgrammingEnvironment,
    hdf5_version: str,
    partition: defs.Partition,
    root_dir: str,
    version: str,
):
    with common.utils.batch_file(filename="build_netcdf"):
        utils.setup_env(env, partition)
        common.utils_module.module_load("cray-mpich")
        root_dir = os.path.abspath(root_dir)
        hdf5_root = os.path.join(root_dir, "hdf5", hdf5_version, "build", env)
        common.utils.export_variable("HDF5_ROOT", hdf5_root)
        with common.utils.chdir(root_dir):
            os.makedirs("netcdf-c", exist_ok=True)
            branch = f"v{version}"
            common.utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/Unidata/netcdf-c.git netcdf-c/{version}"
            )
            with common.utils.chdir(f"netcdf-c/{version}"):
                common.utils.run("autoupdate")
                common.utils.run("autoreconf -if")
                common.utils.run("rm -rf build")
                build_dir = os.path.join(root_dir, f"netcdf-c/{version}/build/{env}")
                hdf5_include_dir = os.path.join(hdf5_root, "include")
                hdf5_lib_dir = os.path.join(hdf5_root, "lib")
                common.utils.run(
                    "CC=cc",
                    f"CFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"CPPFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"LDFLAGS='-fPIC -L{hdf5_lib_dir}'",
                    "LIBS=-ldl",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--disable-shared",
                    "--enable-parallel-tests",
                )
                common.utils.run("make -j 8 install")
                common.utils.export_variable("NETCDF_ROOT", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
