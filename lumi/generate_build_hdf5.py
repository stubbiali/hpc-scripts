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
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
STACK_VERSION: Optional[str] = "23.09"
VERSION: str = "1.14.4.3"
# >>> config: end


def core(
    compiler_version: str,
    env: defs.ProgrammingEnvironment,
    env_version: str,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with utils.batch_file(prefix="build_hdf5"):
        utils.module_reset()
        utils.load_stack(stack, stack_version)
        utils.load_partition(partition_type)
        env, cpe = utils.load_env(env, env_version, partition_type, stack_version)
        compiler = utils.load_compiler(env, compiler_version)
        utils.module_load("buildtools")
        root_dir = os.path.abspath(os.curdir)
        with utils.chdir(root_dir):
            utils.run("mkdir -p hdf5")
            branch = f"hdf5-{version.replace('.', '_')}" if version < '1.14.4' else f"hdf5_{version}"
            utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/HDFGroup/hdf5.git hdf5/{version}"
            )
            with utils.chdir(f"hdf5/{version}"):
                utils.run("chmod +x autogen.sh")
                utils.run("./autogen.sh")
                build_dir = os.path.join(
                    root_dir,
                    "hdf5",
                    version,
                    "build",
                    stack + "-" + stack_version or "",
                    env + "-" + env_version,
                    compiler.replace("/", "-"),
                )
                utils.run(f"rm -rf {build_dir}")
                utils.run(
                    "CC=cc",
                    "CFLAGS='-fPIC'",
                    "CXX=CC",
                    "CXXFLAGS='-fPIC'",
                    "FC=ftn",
                    "FCFLAGS='-fPIC'",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--enable-build-mode=production",
                    # "--enable-cxx",
                    "--enable-fortran",
                    "--enable-parallel",
                    "--enable-shared=no",
                    "--enable-tests",
                    "--enable-tools",
                )
                utils.run("make -j 8 install")
                utils.export_variable("HDF5_ROOT", build_dir)
                utils.export_variable("HDF5_DIR", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--env-version", type=str, default=ENV_VERSION)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
