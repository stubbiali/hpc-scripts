#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

from hpc_scripts import common
from hpc_scripts.lumi import defaults, defs, make_build_hdf5, utils

if TYPE_CHECKING:
    from typing import Optional


def _get_dir(version: str) -> str:
    return os.path.join(common.config.ROOT_DIR, f"netcdf-c/{version}")


def _get_install_dir(netcdf_dir: str, subtree: str, hdf5_version) -> str:
    return os.path.join(netcdf_dir, "install", subtree, f"hdf5-{hdf5_version}")


def _setup(install_dir: str) -> None:
    common.utils.export_variable("NETCDF_ROOT", install_dir)
    common.utils.export_variable("NETCDF_DIR", install_dir)
    common.utils.export_variable("NETCDF4_DIR", install_dir)


def get_install_dir(
    env: defs.ProgrammingEnvironment,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    hdf5_version: str,
    version: str,
) -> str:
    return _get_install_dir(
        netcdf_dir=_get_dir(version),
        subtree=utils.get_subtree(env, stack, stack_version),
        hdf5_version=hdf5_version,
    )


def setup(
    env: defs.ProgrammingEnvironment,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    hdf5_version: str,
    version: str,
) -> None:
    _setup(install_dir=get_install_dir(env, stack, stack_version, hdf5_version, version))


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

        netcdf_dir = _get_dir(version)
        branch = f"v{version}"
        common.utils.run(
            f"git clone --branch={branch} --depth=1 "
            f"https://github.com/Unidata/netcdf-c.git {netcdf_dir}"
        )

        with common.utils.chdir(netcdf_dir):
            make_build_hdf5.setup(env, stack, stack_version, hdf5_version)

            common.utils.run("autoupdate")
            common.utils.run("autoreconf -if")
            install_dir = _get_install_dir(
                netcdf_dir, utils.get_subtree(env, stack, stack_version), hdf5_version
            )
            common.utils.run(f"rm -rf {install_dir}")
            hdf5_include_dir = os.path.join(
                hdf5_root := make_build_hdf5.get_install_dir(
                    env, stack, stack_version, hdf5_version
                ),
                "include",
            )
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

            _setup(install_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.NETCDF_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)


if __name__ == "__main__":
    main()
