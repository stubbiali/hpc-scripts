#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

import common.utils
import common.utils_module
import defaults
import make_build_hdf5
import utils

if TYPE_CHECKING:
    from typing import Optional

    import defs


def _get_dir(root_dir: str, version: str) -> str:
    return os.path.join(root_dir, f"netcdf-c/{version}")


def _get_install_dir(netcdf_dir: str, subtree: str, hdf5_version) -> str:
    return os.path.join(netcdf_dir, "install", subtree, f"hdf5-{hdf5_version}")


def _setup(install_dir: str) -> None:
    common.utils.export_variable("NETCDF_ROOT", install_dir)
    common.utils.export_variable("NETCDF_DIR", install_dir)
    common.utils.export_variable("NETCDF4_DIR", install_dir)


def setup(
    env: defs.ProgrammingEnvironment,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    hdf5_version: str,
    version: str,
) -> None:
    _setup(
        install_dir=_get_install_dir(
            netcdf_dir=_get_dir(root_dir=make_build_hdf5.get_root_dir(), version=version),
            subtree=utils.get_subtree(env, stack, stack_version),
            hdf5_version=hdf5_version,
        )
    )


def core(
    env: defs.ProgrammingEnvironment,
    hdf5_version: str,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with common.utils.batch_file(filename="build_netcdf"):
        utils.setup_env(env, partition, stack, stack_version)
        common.utils_module.module_load("buildtools")

        root_dir = make_build_hdf5.get_root_dir()
        subtree = utils.get_subtree(env, stack, stack_version)

        hdf5_root = os.path.join(root_dir, "hdf5", hdf5_version, "install", subtree)
        common.utils.export_variable("HDF5_ROOT", hdf5_root)

        with common.utils.chdir(root_dir):
            os.makedirs("netcdf-c", exist_ok=True)
            branch = f"v{version}"
            common.utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/Unidata/netcdf-c.git netcdf-c/{version}"
            )

            with common.utils.chdir(f"netcdf-c/{version}"):
                common.utils.run("autoupdate")
                common.utils.run("autoreconf -if")
                install_dir = os.path.join(
                    root_dir, "netcdf-c", version, "install", subtree, f"hdf5-{hdf5_version}"
                )
                common.utils.run(f"rm -rf {install_dir}")
                hdf5_include_dir = os.path.join(hdf5_root, "include")
                hdf5_lib_dir = os.path.join(hdf5_root, "lib")
                common.utils.run(
                    f"CFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"CPPFLAGS='-fPIC -I{hdf5_include_dir}'",
                    f"LDFLAGS='-fPIC -L{hdf5_lib_dir} -lhdf5'",
                    "LIBS=-ldl",
                    "./configure",
                    f"--prefix={install_dir}",
                    "--disable-libxml2",
                    "--disable-shared",
                    "--enable-parallel-tests",
                )
                common.utils.run("make -j 8 install")

                common.utils.export_variable("NETCDF_ROOT", install_dir)
                common.utils.export_variable("NETCDF4_DIR", install_dir)


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
