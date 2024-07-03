#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import Optional

import defs
import utils


# >>> config: start
BRANCH: str = "gt4py"
COMPILER_VERSION: str = "16.0.1"
ENV: defs.ProgrammingEnvironment = "cray"
ENV_VERSION: str = "8.4.0"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
STACK_VERSION: Optional[str] = "23.09"
# >>> config: end


def core(
    branch: str,
    compiler_version: str,
    env: defs.ProgrammingEnvironment,
    env_version: str,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    project: str = "cloudsc",
) -> str:
    with utils.batch_file(prefix="prepare_" + project) as (f, fname):
        # clear environment
        utils.module_reset()

        # load relevant modules
        utils.load_stack(stack, stack_version)
        utils.load_partition(partition_type)
        env, cpe = utils.load_env(env, env_version, partition_type, stack_version)
        compiler = utils.load_compiler(env, compiler_version)
        utils.module_load(
            "Boost",
            "buildtools",
            "cray-hdf5",
            "cray-python",
            "git",
        )
        if partition_type == "gpu":
            utils.module_load("rocm")

        # patch PYTHONPATH
        utils.export_variable("PYTHONPATH", "/opt/cray/pe/python/3.9.13.1")

        # set path to the source code of the project
        pwd = os.path.abspath(os.environ.get("PROJECT", os.path.curdir))
        project_dir = os.path.join(pwd, project, branch)
        assert os.path.exists(project_dir), f"Branch `{branch}` of `{project} not found."
        utils.export_variable(project.upper(), os.path.join(project_dir, "src", project + "_gt4py"))
        utils.export_variable(
            project.upper() + "_VENV",
            os.path.join(
                project_dir,
                "src",
                project + "_gt4py",
                "venv",
                stack,
                stack_version or "",
                env,
                env_version,
                compiler,
            ),
        )

        # low-level GT4Py and DaCe config
        gt_cache_root = os.path.join(
            project_dir,
            "src",
            project + "_gt4py",
            "gt_cache",
            stack,
            stack_version or "",
            env,
            env_version,
            compiler_version,
        )
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip()

        # required to run OpenACC version (w/o hoisting) on large domains
        # utils.export_variable("PGI_ACC_CUDA_HEAPSIZE", "16GB")

        # path to BOOST
        # utils.export_variable("BOOST_ROOT", os.path.join(pwd, "boost", boost_version))

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--env-version", type=str, default=ENV_VERSION)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    args = parser.parse_args()
    core(**args.__dict__, project="cloudsc")
