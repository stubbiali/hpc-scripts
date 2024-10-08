#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils


# >>> config: start
ENV: defs.ProgrammingEnvironment = "gnu"
PARTITION: defs.Partition = "gpu"
HDF5_VERSION: str = "1.14.2"
ROOT_DIR: str = f"/home/{os.getlogin()}"
VERSION: str = "4.9.2"
# >>> config: end


def core(
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    hdf5_version: str,
    root_dir: str,
    version: str,
):
    with utils.batch_file(prefix="build_netcdf"):
        utils.module_purge(force=True)
        utils.load_env(env)
        utils.module_load("gcc/11.2.0")
        utils.append_to_path("LD_LIBRARY_PATH", f"/usr/local/apps/gcc/11.2.0/lib64")
        utils.module_load("openmpi")
        root_dir = os.path.abspath(root_dir)
        hdf5_root = os.path.join(root_dir, "hdf5", hdf5_version, "build", env)
        utils.export_variable("HDF5_ROOT", hdf5_root)
        with utils.chdir(root_dir):
            os.makedirs("netcdf-c", exist_ok=True)
            branch = f"v{version}"
            utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/Unidata/netcdf-c.git netcdf-c/{version}"
            )
            with utils.chdir(f"netcdf-c/{version}"):
                utils.run("autoupdate")
                utils.run("autoreconf -if")
                utils.run("rm -rf build")
                build_dir = os.path.join(root_dir, f"netcdf-c/{version}/build/{env}")
                hdf5_include_dir = os.path.join(hdf5_root, "include")
                hdf5_lib_dir = os.path.join(hdf5_root, "lib")
                utils.run(
                    "CC=mpicc",
                    "CXX=mpicxx",
                    f"CFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"CPPFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"LDFLAGS='-fPIC -L{hdf5_lib_dir}'",
                    "LIBS=-ldl",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--disable-shared",
                    "--enable-parallel-tests",
                )
                utils.run("make -j 8 install")
                utils.export_variable("NETCDF_ROOT", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
