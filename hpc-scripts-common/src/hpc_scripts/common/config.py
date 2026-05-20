# -*- coding: utf-8 -*-
import os

ROOT_DIR = os.path.abspath(
    os.environ.get(
        "HPC_SCRIPTS_ROOT_DIR", os.environ.get("PROJECT", os.environ.get("HOME", "/tmp"))
    )
)
