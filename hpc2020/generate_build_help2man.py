#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils

# >>> config: start
ENV: defs.ProgrammingEnvironment = "gnu"
COMPILER_VERSION: str = "11.2.0"
ROOT_DIR: str = defs.root_dir
# >>> config: end


def _setup(build_dir: str) -> None:
    utils.update_path(f"{build_dir}/bin")


def core(
    env: defs.ProgrammingEnvironment, compiler_version: str, root_dir: str, _build: bool = True
) -> str:
    with utils.batch_file(prefix="build_help2man"):
        utils.module_purge(force=True)
        utils.load_env(env)
        env_id = utils.load_compiler(env, compiler_version)
        root_dir = os.path.abspath(root_dir)
        build_dir = os.path.join(root_dir, f"help2man/build/{env_id}")

        if _build:
            with utils.chdir(root_dir):
                utils.run("mkdir -p help2man")
                utils.run(
                    f"git clone --branch=master "
                    f"https://github.com/Distrotech/help2man.git help2man"
                )
                with utils.chdir(f"help2man"):
                    utils.run("./configure", f"--prefix={build_dir}")
                    utils.run("make -j 8 install")

        _setup(build_dir)

    return build_dir


def setup(env: defs.ProgrammingEnvironment, compiler_version: str, root_dir: str) -> None:
    build_dir = core(env, compiler_version, root_dir, _build=False)
    _setup(build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    args = parser.parse_args()
    core(**args.__dict__)
