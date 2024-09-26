# -*- coding: utf-8 -*-
from __future__ import annotations
import contextlib
import dataclasses
import os
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING

import defs

if TYPE_CHECKING:
    from typing import Any, Optional


BATCH_DIRECTORY_REGISTRY = []
BATCH_FILE_REGISTRY = []


@contextlib.contextmanager
def batch_directory(path: typing.Optional[str] = None):
    assert len(BATCH_DIRECTORY_REGISTRY) <= 1
    try:
        if len(BATCH_DIRECTORY_REGISTRY) > 0:
            final_cleanup = False
            yield BATCH_DIRECTORY_REGISTRY[-1]
        else:
            final_cleanup = True
            if path is not None:
                path = os.path.abspath(path)
                if os.path.exists(path):
                    shutil.rmtree(path)
                    print(f"py-hpc-scripts: overwrite {path}")
                else:
                    print(f"py-hpc-scripts: create {path}")
                os.makedirs(path)
            else:
                os.makedirs("_tmp", exist_ok=True)
                path = os.path.abspath(tempfile.mkdtemp(dir="_tmp"))
                os.makedirs(path, exist_ok=True)
                print(f"py-hpc-scripts: create {path}")
            BATCH_DIRECTORY_REGISTRY.append(path)
            yield path
    finally:
        if final_cleanup:
            BATCH_DIRECTORY_REGISTRY.pop()


@contextlib.contextmanager
def batch_file(filename: typing.Optional[str] = None):
    if filename is not None:
        if len(BATCH_DIRECTORY_REGISTRY) > 0:
            fname = os.path.abspath(os.path.join(BATCH_DIRECTORY_REGISTRY[-1], filename + ".sh"))
        else:
            # os.makedirs("_tmp", exist_ok=True)
            # fname = os.path.abspath(tempfile.mktemp(prefix=prefix + "_", suffix=".sh", dir="_tmp"))
            fname = os.path.abspath(filename + ".sh")

        try:
            with open(fname, "w") as f:
                BATCH_FILE_REGISTRY.append(f)
                f.write("#!/bin/bash -l\n\n")
                yield f, fname
        finally:
            print(f"py-hpc-scripts: write {fname}")
            BATCH_FILE_REGISTRY.pop()


def run(*args: str, split: bool = False, verbose: bool = False) -> None:
    split_args = [item for arg in args for item in arg.split(" ")]
    if split:
        command = split_args[0]
        for arg in split_args[1:]:
            command += " \\\n    " + arg
    else:
        command = " ".join(split_args)
    if verbose:
        print(command)
    if len(BATCH_FILE_REGISTRY) > 0:
        BATCH_FILE_REGISTRY[-1].write(command + "\n")
    else:
        subprocess.run(command, capture_output=False, shell=True)


def module_reset() -> None:
    run("module reset")


def module_load(*module_names: str) -> None:
    for module_name in module_names:
        if module_name:
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
    if token is not None and token not in options:
        raise InvalidArgumentError(parameter, token, options)
    try:
        yield token
    finally:
        pass


def load_stack(stack: defs.SoftwareStack, stack_version: Optional[str]) -> str:
    with check_argument("stack", stack, defs.valid_software_stacks):
        module = "CrayEnv" if stack == "cray" else stack.upper()
        if stack_version is not None:
            module += f"/{stack_version}"
        module_load(module)
        return module.replace("/", "-")


def get_partition_type(partition: defs.Partition) -> str:
    with check_argument("partition", partition, defs.valid_partitions):
        return defs.PartitionType[partition]


def load_partition(partition: defs.Partition) -> None:
    with check_argument("partition", partition, defs.valid_partitions):
        partition_type = get_partition_type(partition)
        if partition_type == "gpu":
            module_load("partition/G")
        else:
            module_load("partition/C")


def load_cpe(env: defs.ProgrammingEnvironment, stack_version: Optional[str]) -> str:
    with check_argument("env", env, defs.valid_programming_environments):
        if env == "cray":
            cpe = "cpeCray"
        else:
            cpe = "cpe" + env.upper()
        if stack_version is not None:
            cpe += "-" + stack_version
        module_load(cpe.replace("-", "/"))
        return cpe


def setup_env(
    env: defs.ProgrammingEnvironment,
    partition: defs.Partition,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
) -> str:
    module_reset()
    load_stack(stack, stack_version)
    load_partition(partition)
    cpe = load_cpe(env, stack_version)
    return cpe


def export_variable(name: str, value: Any) -> None:
    run(f"export {name}={str(value)}")


def get_subtree(
    env: defs.ProgrammingEnvironment,
    stack: defs.SoftwareStack,
    stack_version: Optional[str],
    ghex_transport_backend: Optional[defs.GHEXTransportBackend] = None,
    rocm_version: Optional[str] = None,
) -> str:
    with check_argument("env", env, defs.valid_programming_environments):
        with check_argument("stack", stack, defs.valid_software_stacks):
            subtree = os.path.join(
                stack + ("-" + stack_version if stack_version else ""),
                env + ("-" + stack_version if stack_version else ""),
            )
            if ghex_transport_backend is not None:
                with check_argument(
                    "ghex_transport_backend",
                    ghex_transport_backend,
                    defs.valid_ghex_transport_backends,
                ):
                    subtree = os.path.join(subtree, ghex_transport_backend)
            if rocm_version is not None:
                subtree = os.path.join(subtree, "rocm-" + rocm_version)
            return subtree


def setup_hip(rocm_version: str) -> None:
    export_variable("CUDA_HOME", f"/opt/rocm-{rocm_version}")
    export_variable("CUPY_ACCELERATORS", "cub")
    export_variable("CUPY_INSTALL_USE_HIP", 1)
    export_variable("GHEX_USE_GPU", 1)
    export_variable("GHEX_GPU_TYPE", "AMD_LEGACY")
    export_variable("GHEX_GPU_ARCH", "gfx90a")
    export_variable("GT4PY_USE_HIP", 1)
    export_variable("HCC_AMDGPU_TARGET", "gfx90a")
    export_variable("ROCM_HOME", f"/opt/rocm-{rocm_version}")


@contextlib.contextmanager
def chdir(dirname: str, restore: bool = True) -> None:
    try:
        run(f"pushd {dirname}")
        yield None
    finally:
        if restore:
            run("popd")


def get_srun_options(
    num_nodes: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    partition: defs.Partition,
    gt_backend: Optional[str] = None,
) -> list[str]:
    srun_options = [
        f"--nodes={num_nodes}",
        f"--ntasks-per-node={num_tasks_per_node}",
        "--distribution=block:block",
    ]
    if (
        get_partition_type(partition) == "gpu"
        and gt_backend in ["cuda", "dace:gpu", "gt:gpu"]
        and num_tasks_per_node == 8
    ):
        # srun_options.append("--cpu-bind=map_cpu:49,57,17,25,1,9,33,41")
        srun_options.append(
            "--cpu-bind=mask_cpu:fe000000000000,fe00000000000000,"
            "fe0000,fe000000,fe,fe00,fe00000000,fe0000000000"
        )
    else:
        srun_options += [f"--cpus-per-task={num_threads_per_task}", "--cpu-bind=cores"]
    return srun_options


@dataclasses.dataclass
class ThreadsLayout:
    num_nodes: int
    num_tasks_per_node: int
    num_threads_per_task: int

    @property
    def num_tasks(self) -> int:
        return self.num_nodes * self.num_tasks_per_node
