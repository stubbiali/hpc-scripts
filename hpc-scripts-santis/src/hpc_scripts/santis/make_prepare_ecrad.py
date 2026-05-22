#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os

from hpc_scripts import common
from hpc_scripts.santis import defaults, defs, make_build_spack_env

# >>> config: start
BRANCH: str = "bench"
# >>> config: end


def core(branch: str, uenv: defs.UEnv) -> str:
    with common.utils.output_file(filename="prepare_ecrad") as (_, fname):
        make_build_spack_env.activate_view("ecrad", uenv)

        # set path to ecrad-porting code
        if not os.path.exists(
            ecrad_dir := os.path.join(common.config.APPS_ROOT_DIR, "ecrad", branch)
        ):
            common.utils.run(
                f"git clone -b {branch} git@github.com:ecmwf-ifs/ecrad.git {ecrad_dir}"
            )
        common.utils.export_variable("ECRAD", ecrad_dir)

        # add netcdf libs to linker and loader path
        common.utils.run("netcdfc_root=$(spack location -i netcdf-c)")
        common.utils.run("netcdff_root=$(spack location -i netcdf-fortran)")
        common.utils.export_variable("LDFLAGS", "-L${netcdfc_root}/lib")
        common.utils.export_variable(
            "LD_LIBRARY_PATH", "${netcdfc_root}/lib:${netcdff_root}/lib:$LD_LIBRARY_PATH"
        )

        with common.utils.chdir(ecrad_dir, restore=False):
            pass

    return fname


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--uenv", type=str, default=defaults.UENV)
    args = parser.parse_args()
    core(**args.__dict__)


if __name__ == "__main__":
    main()
