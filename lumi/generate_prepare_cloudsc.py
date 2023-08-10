#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils


# >>> config: start
BRANCH: str = "gt4py"
ENV: defs.ProgrammingEnvironment = "cray"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
# >>> config: end


def core(
    branch: str,
    env: defs.ProgrammingEnvironment,
    partition_type: defs.PartitionType,
    stack: defs.SoftwareStack,
    project: str = "cloudsc",
) -> str:
    with utils.batch_file(prefix="prepare_" + project) as (f, fname):
        # clear environment
        utils.module_purge(force=True)

        # load relevant modules
        utils.load_stack(stack)
        suffix = utils.load_partition(partition_type)
        cpe = utils.load_env(env)
        utils.module_load(
            f"Boost/1.79.0-{cpe}-22.08", "buildtools", "cray-hdf5", "cray-python", "git"
        )
        if partition_type == "gpu":
            utils.module_load("rocm")

        # patch PYTHONPATH
        utils.export_variable("PYTHONPATH", "/opt/cray/pe/python/3.9.12.1")

        # set path to the source code of the project
        pwd = os.environ.get("PROJECT", os.path.curdir)
        project_dir = os.path.join(pwd, project, branch)
        assert os.path.exists(project_dir), f"Branch `{branch}` of `{project} not found."
        utils.export_variable(project.upper(), project_dir)

        # low-level GT4Py and DaCe config
        gt_cache_root = os.path.join(pwd, f"{project}/src/{project}_gt4py/gt_cache/{env}{suffix}")
        utils.export_variable("GT_CACHE_ROOT", gt_cache_root)
        utils.export_variable("GT_CACHE_DIR_NAME", ".gt_cache")
        utils.export_variable("DACE_CONFIG", os.path.join(gt_cache_root, ".dace.conf"))

        # set/fix HIP-related variables
        if partition_type == "gpu":
            utils.setup_hip()

        # required to run OpenACC version (w/o hoisting) on large domains
        # utils.export_variable("PGI_ACC_CUDA_HEAPSIZE", "16GB")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    args = parser.parse_args()
    core(**args.__dict__, project="cloudsc")
