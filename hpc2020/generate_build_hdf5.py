#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_build_autoconf
import generate_build_help2man
import utils


# >>> config: start
AUTOCONF_VERSION: str = "2.72"
ENV: defs.ProgrammingEnvironment = "gnu"
COMPILER_VERSION: str = "11.2.0"
MPI: defs.MPI = "hpcx"
PARTITION: defs.Partition = "gpu"
ROOT_DIR: str = defs.root_dir
VERSION: str = "1.14.4.2"
# >>> config: end


def _setup(build_dir: str) -> None:
    utils.export_variable("HDF5_DIR", build_dir)
    utils.export_variable("HDF5_ROOT", build_dir)


def core(
    autoconf_version: str,
    env: defs.ProgrammingEnvironment,
    compiler_version: str,
    mpi: defs.MPI,
    partition: defs.Partition,
    root_dir: str,
    version: str,
    _build: bool = True,
) -> str:
    with utils.batch_file(prefix="build_hdf5"):
        utils.module_purge(force=True)
        utils.load_env(env)
        env_id = utils.load_compiler(env, compiler_version)
        mpi_id = utils.load_mpi(mpi, env, compiler_version, partition)
        root_dir = os.path.abspath(root_dir)
        build_dir = os.path.join(root_dir, f"hdf5/{version}/build/{env_id}/{mpi_id}")

        generate_build_help2man.setup(env, compiler_version, root_dir)
        generate_build_autoconf.setup(env, compiler_version, root_dir, autoconf_version)

        if _build:
            with utils.chdir(root_dir):
                utils.run("mkdir -p hdf5")
                branch = (
                    f"hdf5-{version.replace('.', '_')}" if version < "1.14.4" else f"hdf5_{version}"
                )
                utils.run(
                    f"git clone --branch={branch} --depth=1 "
                    f"https://github.com/HDFGroup/hdf5.git hdf5/{version}"
                )
                with utils.chdir(f"hdf5/{version}"):
                    utils.run("chmod +x autogen.sh")
                    utils.run("./autogen.sh")
                    utils.run(
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

        _setup(build_dir)

    return build_dir


def setup(
    autoconf_version: str,
    env: defs.ProgrammingEnvironment,
    compiler_version: str,
    mpi: defs.MPI,
    partition: defs.Partition,
    root_dir: str,
    version: str,
) -> str:
    build_dir = core(
        autoconf_version, env, compiler_version, mpi, partition, root_dir, version, _build=False
    )
    _setup(build_dir)
    return build_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--autoconf-version", type=str, default=AUTOCONF_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--mpi", type=str, default=MPI)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
