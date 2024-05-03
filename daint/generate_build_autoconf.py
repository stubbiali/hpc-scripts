#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import utils


# >>> config: start
ENV: defs.ProgrammingEnvironment = "gnu"
PARTITION: defs.Partition = "gpu"
ROOT_DIR: str = f"/users/{os.getlogin()}"
VERSION: str = "2.72"
# >>> config: end


def core(env: defs.ProgrammingEnvironment, partition: defs.Partition, root_dir: str, version: str):
    with utils.batch_file(prefix="build_autoconf"):
        utils.module_purge(force=True)
        utils.load_partition(partition)
        utils.load_env(env)
        root_dir = os.path.abspath(root_dir)
        with utils.chdir(root_dir):
            utils.run("mkdir -p autoconf")
            branch = f"v{version}"
            utils.run(
                f"git clone --branch={branch} "
                f"http://git.sv.gnu.org/r/autoconf.git autoconf/{version}"
            )
            with utils.chdir(f"autoconf/{version}"):
                utils.run("./bootstrap")
                build_dir = os.path.join(root_dir, f"autoconf/{version}/build/{env}")
                utils.run("CC=cc", "CXX=CC", "./configure", f"--prefix={build_dir}")
                utils.run("make -j 8 install")
                utils.export_variable("AUTOCONF_ROOT", build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--version", type=str, default=VERSION)
    args = parser.parse_args()
    core(**args.__dict__)
