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
        if env == "gnu":
            module_load("prgenv/gnu", "gcc/11.2.0")
            cc, cxx, fc = "gcc", "g++", "gfortran"
            export_variable(
                "LD_LIBRARY_PATH", "/usr/local/apps/gcc/11.2.0/lib64", prepend_value=True
            )
        else:
            module_load("prgenv/intel")
            cc, cxx, fc = "icc", "icpc", "ifort"
        export_variable("CC", cc)
        export_variable("CXX", cxx)
        export_variable("FC", fc)


def load_mpi(env: str, mpi: str, partition: str) -> None:
    with check_argument("env", env, defs.valid_programming_environments):
        with check_argument("mpi", mpi, defs.valid_mpi_libraries):
            with check_argument("partition", partition, defs.valid_partitions):
                cc, cxx, fc = "mpicc", "mpicxx", "mpifort"
                if mpi == "hpcx":
                    module_load("hpcx-openmpi/2.10.0")
                elif mpi == "intel-mpi":
                    module_load("intel-mpi/2023.2.0")
                    if env == "intel":
                        cc, cxx, fc = "mpiicc", "mpiicpc", "mpiifort"
                    else:
                        cc, cxx, fc = "mpigcc", "mpigxx", "mpif90"
                else:
                    if partition == "gpu":
                        module_load("openmpi/4.1.5.4")
                    else:
                        module_load("openmpi/4.1.1.1")
                export_variable("CC", cc)
                export_variable("MPICC", cc)
                export_variable("CXX", cxx)
                export_variable("MPICXX", cxx)
                export_variable("FC", fc)
                export_variable("MPIFC", fc)


def export_variable(name: str, value: typing.Any, prepend_value: bool = False) -> None:
    cmd = f"export {name}={str(value)}"
    if prepend_value:
        cmd += f":${name}"
    run(cmd)


def update_path(value: str):
    export_variable("PATH", value, prepend_value=True)


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
