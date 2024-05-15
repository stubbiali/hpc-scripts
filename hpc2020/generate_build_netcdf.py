#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_build_autoconf
import generate_build_hdf5
import generate_build_help2man
import utils


# >>> config: start
AUTOCONF_VERSION: str = "2.72"
ENV: defs.ProgrammingEnvironment = "gnu"
COMPILER_VERSION: str = "11.2.0"
HDF5_VERSION: str = "1.14.4.2"
MPI: defs.MPI = "hpcx"
PARTITION: defs.Partition = "gpu"
ROOT_DIR: str = defs.root_dir
VERSION: str = "4.9.2"
# >>> config: end


def _setup(build_dir: str) -> None:
    utils.export_variable("NETCDF4_DIR", build_dir)
    utils.export_variable("NETCDF_ROOT", build_dir)


def core(
    autoconf_version: str,
    env: defs.ProgrammingEnvironment,
    compiler_version: str,
    hdf5_version: str,
    mpi: defs.MPI,
    partition: defs.Partition,
    root_dir: str,
    version: str,
    _build: bool = True,
):
    with utils.batch_file(prefix="build_netcdf"):
        utils.module_purge(force=True)
        utils.load_env(env)
        env_id = utils.load_compiler(env, compiler_version)
        mpi_id = utils.load_mpi(mpi, env, compiler_version, partition)
        root_dir = os.path.abspath(root_dir)
        build_dir = os.path.join(root_dir, f"netcdf-c/{version}/build/{env_id}/{mpi_id}")

        generate_build_help2man.setup(env, compiler_version, root_dir)
        generate_build_autoconf.setup(env, compiler_version, root_dir, autoconf_version)
        hdf5_build_dir = generate_build_hdf5.setup(
            autoconf_version, env, compiler_version, mpi, partition, root_dir, hdf5_version
        )

        with utils.chdir(root_dir):
            os.makedirs("netcdf-c", exist_ok=True)
            utils.run(
                f"git clone --branch=v{version} --depth=1 "
                f"https://github.com/Unidata/netcdf-c.git netcdf-c/{version}"
            )
            with utils.chdir(f"netcdf-c/{version}"):
                utils.run("autoupdate")
                utils.run("autoreconf -if")
                utils.run("rm -rf build")
                hdf5_include_dir = os.path.join(hdf5_build_dir, "include")
                hdf5_lib_dir = os.path.join(hdf5_build_dir, "lib")
                utils.run(
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

        _setup(build_dir)

    return build_dir


def setup(
    autoconf_version: str,
    env: defs.ProgrammingEnvironment,
    compiler_version: str,
    hdf5_version: str,
    mpi: defs.MPI,
    partition: defs.Partition,
    root_dir: str,
    version: str,
) -> str:
    build_dir = core(
        autoconf_version,
        env,
        compiler_version,
        hdf5_version,
        mpi,
        partition,
        root_dir,
        version,
        _build=False,
    )
    _setup(build_dir)
    return build_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--autoconf-version", type=str, default=AUTOCONF_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--mpi", type=str, default=MPI)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
