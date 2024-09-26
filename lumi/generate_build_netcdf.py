#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import defaults
import defs
import utils


def core(
    env: defs.ProgrammingEnvironment,
    hdf5_version: str,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with utils.batch_file(filename="build_netcdf"):
        utils.setup_env(env, partition, stack, stack_version)
        utils.module_load("buildtools")

        root_dir = os.path.abspath(os.curdir)
        subtree = utils.get_subtree(env, stack, stack_version)

        hdf5_root = os.path.join(root_dir, "hdf5", hdf5_version, "build", subtree)
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
                build_dir = os.path.join(root_dir, "netcdf-c", version, "build", subtree)
                utils.run(f"rm -rf {build_dir}")
                hdf5_include_dir = os.path.join(hdf5_root, "include")
                hdf5_lib_dir = os.path.join(hdf5_root, "lib")
                utils.run(
                    "CC=cc",
                    "CXX=CC",
                    f"CFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"CPPFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"LDFLAGS='-fPIC -L{hdf5_lib_dir}'",
                    "LIBS=-ldl",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--disable-libxml2",
                    "--disable-shared",
                    "--enable-parallel-tests",
                )
                utils.run("make -j 8 install")

                utils.export_variable("NETCDF_ROOT", build_dir)
                utils.export_variable("NETCDF4_DIR", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.NETCDF_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
