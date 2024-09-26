#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import update_path

import common_utils
import defaults
import defs
import utils


def core(
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with utils.batch_file(filename="build_hdf5"):
        utils.setup_env(env, partition, stack, stack_version)
        common_utils.module_load("buildtools")

        root_dir = os.path.abspath(os.curdir)
        with common_utils.chdir(root_dir):
            common_utils.run("mkdir -p hdf5")
            branch = (
                f"hdf5-{version.replace('.', '_')}" if version < "1.14.4" else f"hdf5_{version}"
            )
            common_utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/HDFGroup/hdf5.git hdf5/{version}"
            )

            with common_utils.chdir(f"hdf5/{version}"):
                common_utils.run("chmod +x autogen.sh")
                common_utils.run("./autogen.sh")
                build_dir = os.path.join(
                    root_dir, "hdf5", version, "build", utils.get_subtree(env, stack, stack_version)
                )
                common_utils.run(f"rm -rf {build_dir}")
                common_utils.run(
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
                common_utils.run("make -j 8 install")

                common_utils.export_variable("HDF5_ROOT", build_dir)
                common_utils.export_variable("HDF5_DIR", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.HDF5_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
