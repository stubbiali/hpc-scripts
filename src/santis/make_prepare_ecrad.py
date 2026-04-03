#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os

import common
import defaults
import defs

# >>> config: start
BRANCH: str = "bench"
# >>> config: end


def core(branch: str, uenv: defs.UEnv) -> str:
    with common.utils.batch_file(filename="prepare_ecrad") as (_, fname):
        common.utils.run(
            f". {defs.uenv_spack_builds_root}/"
            f"{uenv.replace('/', '-').replace(':', '-')}/"
            f"ecrad/view/activate.sh"
        )

        # set path to ecrad-porting code
        ecrad_root = os.path.join(defs.scratch_dir, "ecrad")
        ecrad_dir = os.path.join(ecrad_root, branch)
        assert os.path.exists(ecrad_dir)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--uenv", type=str, default=defaults.UENV)
    args = parser.parse_args()
    core(**args.__dict__)
