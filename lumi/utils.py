# -*- coding: utf-8 -*-
from __future__ import annotations
import contextlib
import dataclasses
import os
import subprocess
import tempfile
import typing

import defs


BATCH_DIRECTORY_REGISTRY = []
BATCH_FILE_REGISTRY = []


@contextlib.contextmanager
def batch_directory():
    os.makedirs("_tmp", exist_ok=True)
    try:
        if len(BATCH_DIRECTORY_REGISTRY) > 0:
            final_cleanup = False
            yield BATCH_DIRECTORY_REGISTRY[-1]
        else:
            final_cleanup = True
            dirname = os.path.abspath(tempfile.mkdtemp(dir="_tmp"))
            BATCH_DIRECTORY_REGISTRY.append(dirname)
            os.makedirs(dirname, exist_ok=True)
            print(f"py-hpc-scripts: create {dirname}")
            yield dirname
    finally:
        if final_cleanup:
            BATCH_DIRECTORY_REGISTRY.pop()


@contextlib.contextmanager
def batch_file(prefix: typing.Optional[str] = None):
    if len(BATCH_DIRECTORY_REGISTRY) > 0:
        fname = os.path.abspath(os.path.join(BATCH_DIRECTORY_REGISTRY[-1], prefix + ".sh"))
    else:
        # os.makedirs("_tmp", exist_ok=True)
        # fname = os.path.abspath(tempfile.mktemp(prefix=prefix + "_", suffix=".sh", dir="_tmp"))
        fname = os.path.abspath(prefix + ".sh")

    try:
        with open(fname, "w") as f:
            BATCH_FILE_REGISTRY.append(f)
            f.write("#!/bin/bash -l\n\n")
            yield f, fname
    finally:
        print(f"py-hpc-scripts: write {fname}")
        BATCH_FILE_REGISTRY.pop()


def run(*args: str) -> None:
    split_args = [item for arg in args for item in arg.split(" ")]
    command = " ".join(split_args)
    if len(BATCH_FILE_REGISTRY) > 0:
        BATCH_FILE_REGISTRY[-1].write(command + "\n")
    else:
        subprocess.run(command, capture_output=False, shell=True)


def module_purge(force: bool = False) -> None:
    run(f"module{' --force ' if force else ' '}purge")


def module_load(*module_names: str) -> None:
    for module_name in module_names:
        run(f"module load {module_name}")


class InvalidArgumentError(Exception):
    def __init__(self, parameter: str, token: str, options: list[str]):
        options = [f"`{opt}`" for opt in options]
        msg = (
            f"Invalid value `{token}` for parameter `{parameter}`. "
            f"Available options: {', '.join(options)}."
        )
        super().__init__(msg)


@contextlib.contextmanager
def check_argument(parameter, token, options):
    if token not in options:
        raise InvalidArgumentError(parameter, token, options)
    try:
        yield token
    finally:
        pass


def get_partition(partition_type: typing.Literal["gpu", "host"]) -> str:
    with check_argument("partition_type", partition_type, defs.valid_partition_types):
        if partition_type == "gpu":
            return "standard-g"
        else:
            return "standard"


def load_stack(stack: str) -> None:
    with check_argument("stack", stack, defs.valid_software_stacks):
        if stack == "cray":
            module_load("CrayEnv")
        else:
            module_load("LUMI/22.08")


def load_partition(partition_type: str) -> str:
    with check_argument("partition_type", partition_type, defs.valid_partition_types):
        if partition_type == "gpu":
            module_load("partition/G")
            suffix = ""
        else:
            module_load("partition/C")
            suffix = "-host"
        return suffix


def load_env(env: str) -> str:
    with check_argument("env", env, defs.valid_programming_environments):
        if env == "amd":
            module_load("PrgEnv-amd")
            cpe = "cpeAMD"
        elif env == "cray":
            module_load("PrgEnv-cray")
            cpe = "cpeCray"
        else:
            module_load("PrgEnv-gnu")
            cpe = "cpeGNU"
        return cpe


def export_variable(name: str, value: typing.Any) -> None:
    run(f"export {name}={str(value)}")


def setup_hip():
    export_variable("CUDA_HOME", "/opt/rocm")
    export_variable("CUPY_INSTALL_USE_HIP", 1)
    export_variable("GT4PY_USE_HIP", 1)
    export_variable("HCC_AMDGPU_TARGET", "gfx90a")
    export_variable("ROCM_HOME", "/opt/rocm")


@contextlib.contextmanager
def chdir(dirname: str) -> None:
    try:
        run(f"pushd {dirname}")
        yield None
    finally:
        run("popd")


def get_srun_options(
    num_nodes: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    partition_type: defs.PartitionType,
) -> list[str]:
    srun_options = [
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        "--distribution=block:block",
    ]
    if partition_type == "gpu":
        # srun_options.append("--cpu-bind=map_cpu:49,57,17,25,1,9,33,41")
        srun_options.append(
            "--cpu-bind=mask_cpu:fe000000000000,fe00000000000000,"
            "fe0000,fe000000,fe,fe00,fe00000000,fe0000000000"
        )
    else:
        srun_options.append(f"--cpus-per-task={num_threads_per_task}")
    return srun_options


@dataclasses.dataclass
class ThreadsLayout:
    num_nodes: int
    num_tasks_per_node: int
    num_threads_per_task: int
