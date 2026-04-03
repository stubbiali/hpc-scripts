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
BRANCH: str = "main"
# >>> config: end


def core(
    branch: str,
    ghex_transport_backend: defs.GHEXTransportBackend,
    python_version: defs.PythonVersion,
    uenv: defs.UEnv,
) -> str:
    with common.utils.batch_file(filename="prepare_pmap_les") as (_, fname):
        common.utils.run(
            f". {defs.uenv_spack_builds_root}/"
            f"{(uenv_with_dashes := uenv.replace('/', '-').replace(':', '-'))}/"
            f"pmap-les/view/activate.sh"
        )

        utils.setup_mpi()
        utils.setup_ghex(ghex_transport_backend)

        pmap_root = os.path.join(defs.scratch_dir, "pmap-les")
        pmap_dir = os.path.join(pmap_root, branch)
        assert os.path.exists(pmap_dir)
        common.utils.export_variable("PMAP", pmap_dir)

        common.utils.export_variable(
            "GT_CACHE_ROOT",
            (gt_cache_root := os.path.join(pmap_root, "_gtcache", uenv_with_dashes)),
        )
        # common.utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=4096'")
        common.utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        with common.utils.chdir(pmap_dir, restore=False):
            venv_dir = os.path.join(
                pmap_dir, "_venv", uenv_with_dashes, f"py{python_version.replace('.', '')}"
            )
            common.utils.export_variable("PMAP_VENV", venv_dir)
            if not os.path.exists(venv_dir):
                utils.setup_uv(uenv)
                common.utils.run(f"uv venv --python=$(which python{python_version}) {venv_dir}")
                common.utils.run(f". {venv_dir}/bin/activate")
                common.utils.run(
                    f"uv pip install -e "
                    f".[dev,gpu{'-cuda12x' if python_version < '3.14' else ''},mpi-test]"
                )
            else:
                common.utils.run(f". {venv_dir}/bin/activate")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument(
        "--ghex-transport-backend", type=str, default=defaults.GHEX_TRANSPORT_BACKEND
    )
    parser.add_argument("--python", type=str, default=defaults.PYTHON_VERSION)
    parser.add_argument("--uenv", type=str, default=defaults.UENV)
    args = parser.parse_args()
    core(**args.__dict__)
