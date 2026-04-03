#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os

import common
import defaults
import defs
import utils

# >>> config: start
BRANCH: str = "cy49r1s-pmap"
# >>> config: end


def core(branch: str, python_version: defs.PythonVersion, uenv: defs.UEnv) -> str:
    with common.utils.batch_file(filename="prepare_ecrad_porting") as (_, fname):
        common.utils.run(
            f". {defs.uenv_spack_builds_root}/"
            f"{(uenv_with_dashes := uenv.replace('/', '-').replace(':', '-'))}/"
            f"ecrad/view/activate.sh"
        )

        # set path to ecrad-porting code
        ecrad_root = os.path.join(defs.scratch_dir, "ecrad-porting")
        ecrad_dir = os.path.join(ecrad_root, branch)
        assert os.path.exists(ecrad_dir)
        common.utils.export_variable("ECRAD", ecrad_dir)

        common.utils.export_variable(
            "GT_CACHE_ROOT",
            (gt_cache_root := os.path.join(ecrad_root, "_gtcache", uenv_with_dashes)),
        )
        # common.utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=4096'")
        common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        with common.utils.chdir(ecrad_dir, restore=False):
            venv_dir = os.path.join(
                ecrad_dir, "_venv", uenv_with_dashes, f"py{python_version.replace('.', '')}"
            )
            common.utils.export_variable("ECRAD_VENV", venv_dir)
            if not os.path.exists(venv_dir):
                utils.setup_uv(uenv)
                common.utils.run(f"uv venv --python=$(which python{python_version}) {venv_dir}")
                common.utils.run(f". {venv_dir}/bin/activate")
                common.utils.run(
                    f"uv pip install -e .[dev,gpu{'-cuda12x' if python_version < '3.14' else ''}]"
                )
            else:
                common.utils.run(f". {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--python", type=str, default=defaults.PYTHON_VERSION)
    parser.add_argument("--uenv", type=str, default=defaults.UENV)
    args = parser.parse_args()
    core(**args.__dict__)
