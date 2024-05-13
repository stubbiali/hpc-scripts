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
ROOT_DIR: str = f"/home/{os.getlogin()}"
VERSION: str = "1.14.2"
# >>> config: end


def core(
    env: defs.ProgrammingEnvironment, partition: defs.Partition, root_dir: str, version: str
):
    with utils.batch_file(prefix="build_hdf5"):
        utils.module_purge(force=True)
        utils.load_env(env)
        utils.module_load("gcc/11.2.0")
        utils.append_to_path("LD_LIBRARY_PATH", f"/usr/local/apps/gcc/11.2.0/lib64")
        utils.module_load("openmpi")
        root_dir = os.path.abspath(root_dir)
        with utils.chdir(root_dir):
            utils.run("mkdir -p hdf5")
            branch = f"hdf5-{version.replace('.', '_')}"
            utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/HDFGroup/hdf5.git hdf5/{version}"
            )
            with utils.chdir(f"hdf5/{version}"):
                utils.run("chmod +x autogen.sh")
                utils.run("./autogen.sh")
                build_dir = os.path.join(root_dir, f"hdf5/{version}/build/{env}")
                utils.run(
                    "CC=mpicc",
                    "CXX=mpicxx",
                    "CFLAGS='-fPIC'",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--enable-build-mode=production",
                    "--enable-parallel",
                    "--enable-shared=no",
                    "--enable-tests",
                    "--enable-tools",
                )
                utils.run("make -j 8 install")
                utils.export_variable("HDF5_ROOT", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
