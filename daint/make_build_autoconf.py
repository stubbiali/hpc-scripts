#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import update_path  # noqa: F401

import common_utils
import defs
import utils


# >>> config: start
ENV: defs.ProgrammingEnvironment = "gnu"
PARTITION: defs.Partition = "gpu"
ROOT_DIR: str = f"/users/{os.getlogin()}"
VERSION: str = "2.72"
# >>> config: end


def core(env: defs.ProgrammingEnvironment, partition: defs.Partition, root_dir: str, version: str):
    with common_utils.batch_file(filename="build_autoconf"):
        utils.setup_env(env, partition)
        root_dir = os.path.abspath(root_dir)
        with common_utils.chdir(root_dir):
            common_utils.run("mkdir -p autoconf")
            branch = f"v{version}"
            common_utils.run(
                f"git clone --branch={branch} "
                f"http://git.sv.gnu.org/r/autoconf.git autoconf/{version}"
            )
            with common_utils.chdir(f"autoconf/{version}"):
                common_utils.run("./bootstrap")
                build_dir = os.path.join(root_dir, f"autoconf/{version}/build/{env}")
                common_utils.run("CC=cc", "CXX=CC", "./configure", f"--prefix={build_dir}")
                common_utils.run("make -j 8 install")
                common_utils.export_variable("AUTOCONF_ROOT", build_dir)
                common_utils.append_to_path("PATH", f"{build_dir}/bin")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
