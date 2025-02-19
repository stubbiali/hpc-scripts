#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

import common.utils
import defaults
import utils

if TYPE_CHECKING:
    import defs


# >>> config: start
ROOT_DIR: str = f"/users/{os.getlogin()}"
VERSION: str = "1.49.3"
# >>> config: endi


def core(env: defs.ProgrammingEnvironment, partition: defs.Partition, root_dir: str, version: str):
    with common.utils.batch_file(filename="build_help2man"):
        utils.setup_env(env, partition)
        root_dir = os.path.abspath(root_dir)
        with common.utils.chdir(root_dir):
            common.utils.run("mkdir -p help2man")
            branch = "master"
            common.utils.run(
                f"git clone --branch={branch} "
                f"https://github.com/Distrotech/help2man.git help2man/{version}"
            )
            with common.utils.chdir(f"help2man/{version}"):
                build_dir = os.path.join(root_dir, f"help2man/{version}/build/{env}")
                common.utils.run("CC=cc", "CXX=CC", "./configure", f"--prefix={build_dir}")
                common.utils.run("make -j 8 install")
                common.utils.append_to_path("PATH", f"{build_dir}/bin")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
