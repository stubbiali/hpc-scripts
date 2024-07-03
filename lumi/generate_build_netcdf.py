#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import defs
import utils


# >>> config: start
COMPILER_VERSION: str = "16.0.1"
ENV: defs.ProgrammingEnvironment = "cray"
ENV_VERSION: str = "8.4.0"
HDF5_VERSION: str = "1.14.4.3"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
STACK_VERSION: Optional[str] = "23.09"
VERSION: str = "4.9.2"
# >>> config: end


def core(
    compiler_version: str,
    env: defs.ProgrammingEnvironment,
    env_version: str,
    hdf5_version: str,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with utils.batch_file(prefix="build_netcdf"):
        utils.module_reset()
        utils.load_stack(stack, stack_version)
        utils.load_partition(partition_type)
        env, cpe = utils.load_env(env, env_version, partition_type, stack_version)
        compiler = utils.load_compiler(env, compiler_version)
        utils.module_load("buildtools")
        root_dir = os.path.abspath(os.curdir)
        subtree = os.path.join(
            stack + "-" + stack_version or "", env + "-" + env_version, compiler.replace("/", "-")
        )
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
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--env-version", type=str, default=ENV_VERSION)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
