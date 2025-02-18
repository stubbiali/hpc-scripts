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


def load_env(env: str) -> None:
    with check_argument("env", env, defs.valid_programming_environments):
        module_load("prgenv/gnu")


def export_variable(name: str, value: typing.Any) -> None:
    run(f"export {name}={str(value)}")


def append_to_path(name: str, value: typing.Any) -> None:
    run(f"{name}={str(value)}:${name}")


def setup_cuda():
    run("NVCC_PATH=$(which nvcc)")
    run("CUDA_PATH=$(echo $NVCC_PATH | sed -e 's/\/bin\/nvcc//g')")
    export_variable("CUDA_HOME", "$CUDA_PATH")
    export_variable("NVHPC_CUDA_HOME", "$CUDA_PATH")
    export_variable("LD_LIBRARY_PATH", "$CUDA_PATH/lib64:$LD_LIBRARY_PATH")


@contextlib.contextmanager
def chdir(dirname: str, restore: bool = True) -> None:
    try:
        run(f"pushd {dirname}")
        yield None
    finally:
        if restore:
            run("popd")


@dataclasses.dataclass
class ThreadsLayout:
    num_nodes: int
    num_tasks_per_node: int
    num_threads_per_task: int
