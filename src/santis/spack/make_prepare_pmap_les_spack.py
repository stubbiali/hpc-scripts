#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os

import common
import defs

# >>> config: start
BRANCH: str = "main"
# >>> config: end


def core(branch: str) -> str:
    with common.utils.batch_file(filename="prepare_pmap_les") as (_, fname):
        common.utils.run(f". {os.path.join(defs.spack_pmap_root, 'share/spack/setup-env.sh')}")
        common.utils.run(f"spack env activate {defs.spack_pmap_env}")

        pwd = os.path.abspath(os.environ.get("SCRATCH", os.path.curdir))
        pmap_root = os.path.join(pwd, "pmap-les")
        pmap_dir = os.path.join(pmap_root, branch)
        assert os.path.exists(pmap_dir)
        common.utils.export_variable("PMAP", pmap_dir)

        common.utils.export_variable(
            "GT_CACHE_ROOT", (gt_cache_root := os.path.join(pmap_root, "_gtcache"))
        )
        # common.utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=4096'")
        common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        with common.utils.chdir(pmap_dir, restore=False):
            venv_dir = os.path.join(pmap_dir, "_venv", defs.spack_pmap_env)
            common.utils.export_variable("PMAP_VENV", venv_dir)
            if not os.path.exists(venv_dir):
                common.utils.run(f"uv venv --system-site-packages {venv_dir}")
                common.utils.run(f". {venv_dir}/bin/activate")
                common.utils.run("uv pip install -e .[dev,test]")
            else:
                common.utils.run(f". {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    args = parser.parse_args()
    core(**args.__dict__)
