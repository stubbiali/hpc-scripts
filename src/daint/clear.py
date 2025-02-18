#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import utils


def core():
    folders = [
        "'*'",
        "_error",
        "_output",
        "_tmp",
        "apps",
        "bin",
        "boot",
        "core",
        "cray",
        "cvmfs",
        "dev",
        "etc",
        "home",
        "home",
        "init",
        "lib",
        "lib64",
        "mnt",
        "opt",
        "proc",
        "project",
        "root",
        "run",
        "sbin",
        "scratch",
        "selinux",
        "srv",
        "store",
        "sys",
        "tmp",
        "users",
        "usr",
        "var",
    ]
    for folder in folders:
        utils.run(f"rm -rf {folder}")


if __name__ == "__main__":
    core()
