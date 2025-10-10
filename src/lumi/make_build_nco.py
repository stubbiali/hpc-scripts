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
    hdf5_version: str,
    netcdf_version: str,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with common.utils.batch_file(filename="build_nco"):
        utils.setup_env(env, partition, stack, stack_version)
        common.utils_module.module_load("buildtools")

        pwd = os.path.abspath(os.environ.get("PROJECT", os.path.curdir))
        nco_dir = os.path.join(pwd, "nco", version)
        with common.utils.chdir(pwd):
            if not os.path.exists(nco_dir):
                common.utils.run("mkdir -p nco")
                common.utils.run(f"wget https://github.com/nco/nco/archive/{version}.tar.gz")
                common.utils.run(f"tar xvzf {version}.tar.gz")
                common.utils.run(f"mv nco-{version} {nco_dir}")
                common.utils.run(f"rm -rf {version}.tar.gz")

            subtree = utils.get_subtree(env, stack, stack_version)
            hdf5_root = os.path.join(pwd, "hdf5", hdf5_version, "build", subtree)
            with common.utils.chdir(nco_dir):
                common.utils.export_variable(
                    "NETCDF_ROOT",
                    (
                        netcdf_root := os.path.join(
                            pwd, "netcdf-c", netcdf_version, "build", subtree
                        )
                    ),
                )
                common.utils.export_variable("NETCDF_INC", os.path.join(netcdf_root, "include"))
                common.utils.export_variable("NETCDF_LIB", os.path.join(netcdf_root, "lib"))
                common.utils.append_to_path("LD_LIBRARY_PATH", os.path.join(hdf5_root, "lib"))
                build_dir = os.path.join(nco_dir, "build", subtree)
                common.utils.run(f"rm -rf {build_dir}")
                common.utils.run(
                    f"LDFLAGS='-L{os.path.join(hdf5_root, 'lib')} -lcurl -lhdf5 -lhdf5_hl -lz'",
                    "./configure",
                    f"--prefix={build_dir}",
                    "--enable-udunits=no",  # disable units support for now
                    "--enable-udunits2=no",  # disable units support for now
                )
                common.utils.run("make -j 8 install")

                common.utils.export_variable("NCO_ROOT", build_dir)
                common.utils.export_variable("NCO_DIR", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=defaults.NETCDF_VERSION)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.NCO_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
