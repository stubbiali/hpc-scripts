#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import update_path  # noqa: F401

import common.utils as common_utils
import defs
import utils


# >>> config: start
ENV: defs.ProgrammingEnvironment = "gnu"
PARTITION: defs.Partition = "gpu"
ROOT_DIR: str = f"/users/{os.getlogin()}"
VERSION: str = "1.14.4.2"
# >>> config: end


def core(env: defs.ProgrammingEnvironment, partition: defs.Partition, root_dir: str, version: str):
    with common_utils.batch_file(filename="build_hdf5"):
        utils.setup_env(env, partition)
        common_utils.module_load("cray-mpich")
        root_dir = os.path.abspath(root_dir)
        with common_utils.chdir(root_dir):
            common_utils.run("mkdir -p hdf5")
            # branch = f"hdf5-{version.replace('.', '_')}"
            branch = f"hdf5_{version}"
            common_utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/HDFGroup/hdf5.git hdf5/{version}"
            )
            with common_utils.chdir(f"hdf5/{version}"):
                common_utils.run("chmod +x autogen.sh")
                common_utils.run("./autogen.sh")
                build_dir = os.path.join(root_dir, f"hdf5/{version}/build/{env}")
                common_utils.run(
                    "CC=cc",
                    "CFLAGS='-fPIC'",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--enable-build-mode=production",
                    "--enable-parallel",
                    "--enable-shared=no",
                    "--enable-tests",
                    "--enable-tools",
                )
                common_utils.run("make -j 8 install")
                common_utils.export_variable("HDF5_ROOT", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
