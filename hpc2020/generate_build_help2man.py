#!/usr/local/apps/python3/3.11.8-01/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils

# >>> config: start
ENV: defs.ProgrammingEnvironment = "gnu"
ROOT_DIR: str = defs.root_dir
# >>> config: end


def core(env: defs.ProgrammingEnvironment, root_dir: str):
    with utils.batch_file(prefix="build_help2man"):
        utils.module_purge(force=True)
        utils.load_env(env)
        root_dir = os.path.abspath(root_dir)
        with utils.chdir(root_dir):
            utils.run("mkdir -p help2man")
            utils.run(
                f"git clone --branch=master " f"https://github.com/Distrotech/help2man.git help2man"
            )
            with utils.chdir(f"help2man"):
                build_dir = os.path.join(root_dir, f"help2man/build/{env}")
                utils.run("./configure", f"--prefix={build_dir}")
                utils.run("make -j 8 install")
                utils.export_variable("PATH", f"{build_dir}/bin", prepend_value=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    args = parser.parse_args()
    core(**args.__dict__)
