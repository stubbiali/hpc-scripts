#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import update_path

import common_utils
import defaults
import defs
import utils


# >>> config: start
BRANCH: str = "gt4py"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    rocm_version: str,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    project: str = "cloudsc",
) -> str:
    with common_utils.batch_file(filename="prepare_" + project) as (f, fname):
        # clear environment
        common_utils.module_reset()

        # load relevant modules
        cpe = utils.setup_env(env, partition, stack, stack_version)
        utils.module_load(f"Boost/1.83.0-{cpe}", "buildtools", "cray-hdf5", "cray-python", "git")
        partition_type = utils.get_partition_type(partition)
        if partition_type == "gpu":
            utils.module_load(f"rocm/{rocm_version}")

        # set path to the source code of the project
        pwd = os.path.abspath(os.environ.get("PROJECT", os.path.curdir))
        project_dir = os.path.join(pwd, project, branch)
        assert os.path.exists(project_dir), f"Branch `{branch}` of `{project} not found."
        common_utils.export_variable(
            project.upper(), os.path.join(project_dir, "src", project + "_gt4py")
        )
        common_utils.export_variable(
            project.upper() + "_VENV",
            os.path.join(
                project_dir,
                "src",
                project + "_gt4py",
                "_venv",
                utils.get_subtree(env, stack, stack_version),
            ),
        )

        # low-level GT4Py and DaCe config
        gt_cache_root = os.path.join(
            project_dir,
            "src",
            project + "_gt4py",
            "_gtcache",
            utils.get_subtree(env, stack, stack_version),
        )
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip(rocm_version)

        # required to run OpenACC version (w/o hoisting) on large domains
        # utils.export_variable("PGI_ACC_CUDA_HEAPSIZE", "16GB")

        # path to BOOST
        # utils.export_variable("BOOST_ROOT", os.path.join(pwd, "boost", boost_version))

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--rocm-version", type=str, default=defaults.ROCM_VERSION)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    args = parser.parse_args()
    core(**args.__dict__, project="cloudsc")
