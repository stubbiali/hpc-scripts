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
        hdf5_dir = os.path.join(root_dir, f"hdf5/{version}")
        with common.utils.chdir(root_dir):
            common.utils.run("mkdir -p hdf5")
            if version < "1.14.4":
                branch = f"hdf5-{version.replace('.', '_')}"
            elif version < "2.0.0":
                branch = f"hdf5_{version}"
            else:
                branch = version
            common.utils.run(
                f"git clone --branch={branch} --depth=1 "
                f"https://github.com/HDFGroup/hdf5.git {hdf5_dir}"
            )

            with common.utils.chdir(hdf5_dir):
                build_dir = os.path.join(
                    hdf5_dir, "build", subtree := utils.get_subtree(env, stack, stack_version)
                )

                if version < "2.0.0":
                    common.utils.run("chmod +x autogen.sh")
                    common.utils.run("./autogen.sh")
                    common.utils.run(f"rm -rf {build_dir}")
                    common.utils.run(
                        "CFLAGS='-fPIC'",
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
                else:
                    install_dir = os.path.join(hdf5_dir, "install", subtree)
                    common.utils.run(f"mkdir -p {build_dir}")
                    with common.utils.chdir(build_dir):
                        common.utils.run(
                            f"cmake {hdf5_dir} "
                            "-DCMAKE_BUILD_TYPE:STRING=Release "
                            f"-DCMAKE_INSTALL_PREFIX:STRING={install_dir} "
                            "-DBUILD_SHARED_LIBS:BOOL=OFF "
                            "-DBUILD_TESTING:BOOL=ON "
                            # note: the following requires MFU, which is not found
                            # "-DHDF5_BUILD_PARALLEL_TOOLS:BOOL=ON"
                            "-DHDF5_BUILD_TOOLS:BOOL=ON"
                            "-DHDF5_ENABLE_FORTRAN:BOOL=ON "
                            "-DHDF5_ENABLE_PARALLEL:BOOL=ON "
                            "-DHDF5_ENABLE_ZLIB_SUPPORT:BOOL=ON "
                        )
                        common.utils.run("make -j 8 install")

                common.utils.export_variable("HDF5_ROOT", install_dir)
                common.utils.export_variable("HDF5_DIR", install_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.HDF5_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
