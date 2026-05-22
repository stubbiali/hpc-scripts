#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
from typing import TYPE_CHECKING

from hpc_scripts import common
from hpc_scripts.lumi import defaults, defs, utils

if TYPE_CHECKING:
    from typing import Optional


def _get_dir(version: str) -> str:
    return os.path.join(common.config.ROOT_DIR, f"hdf5/{version}")


def _get_build_dir(hdf5_dir: str, subtree: str) -> str:
    return os.path.join(hdf5_dir, "build", subtree)


def _get_install_dir(hdf5_dir: str, subtree: str) -> str:
    return os.path.join(hdf5_dir, "install", subtree)


def _setup(install_dir: str) -> None:
    common.utils.export_variable("HDF5_ROOT", install_dir)
    common.utils.export_variable("HDF5_DIR", install_dir)
    common.utils.export_variable(
        "LDFLAGS", f"'-L{os.path.join(install_dir, 'lib')} -lcurl -lhdf5 -lhdf5_hl'"
    )


def get_install_dir(
    env: defs.ProgrammingEnvironment,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> str:
    return _get_install_dir(
        hdf5_dir=_get_dir(version), subtree=utils.get_subtree(env, stack, stack_version)
    )


def setup(
    env: defs.ProgrammingEnvironment,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    _setup(install_dir=get_install_dir(env, stack, stack_version, version))


def core(
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    version: str,
) -> None:
    with common.utils.output_file(filename="build_hdf5"):
        utils.setup_env(env, partition, stack, stack_version)
        common.utils_module.module_load("buildtools")

        hdf5_dir = _get_dir(version)
        if version < "1.14.4":
            branch = f"hdf5-{version.replace('.', '_')}"
        elif version < "2.0.0":
            branch = f"hdf5_{version}"
        else:
            branch = version
        common.utils.run(
            f"git clone --branch={branch} --depth=1 https://github.com/HDFGroup/hdf5.git {hdf5_dir}"
        )

        with common.utils.chdir(hdf5_dir):
            build_dir = _get_build_dir(
                hdf5_dir, subtree := utils.get_subtree(env, stack, stack_version)
            )
            install_dir = _get_install_dir(hdf5_dir, subtree)

            if version < "2.0.0":
                common.utils.run("chmod +x autogen.sh")
                common.utils.run("./autogen.sh")
                common.utils.run(f"rm -rf {install_dir}")
                common.utils.run(
                    "CFLAGS='-fPIC'",
                    "CXXFLAGS='-fPIC'",
                    "FC=ftn",
                    "FCFLAGS='-fPIC'",
                    "./configure",
                    f"--prefix={install_dir}",
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

            _setup(install_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--version", type=str, default=defaults.HDF5_VERSION)
    args = parser.parse_args()
    core(**args.__dict__)


if __name__ == "__main__":
    main()
