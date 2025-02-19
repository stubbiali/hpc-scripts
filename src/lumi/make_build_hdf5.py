#!/opt/cray/pe/python/3.11.7/bin/python
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
    from typing import Optional

    import defs


def core(
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with common.utils.batch_file(filename="build_hdf5"):
        utils.setup_env(env, partition, stack, stack_version)
        common.utils_module.module_load("buildtools")

        root_dir = os.path.abspath(os.curdir)
        with common.utils.chdir(root_dir):
            common.utils.run("mkdir -p hdf5")
            branch = (
                f"hdf5-{version.replace('.', '_')}" if version < "1.14.4" else f"hdf5_{version}"
            )
            common.utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/HDFGroup/hdf5.git hdf5/{version}"
            )

            with common.utils.chdir(f"hdf5/{version}"):
                common.utils.run("chmod +x autogen.sh")
                common.utils.run("./autogen.sh")
                build_dir = os.path.join(
                    root_dir, "hdf5", version, "build", utils.get_subtree(env, stack, stack_version)
                )
                common.utils.run(f"rm -rf {build_dir}")
                common.utils.run(
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
                common.utils.run("make -j 8 install")

                common.utils.export_variable("HDF5_ROOT", build_dir)
                common.utils.export_variable("HDF5_DIR", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.HDF5_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
