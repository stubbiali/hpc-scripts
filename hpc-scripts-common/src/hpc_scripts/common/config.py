# -*- coding: utf-8 -*-
import os

default_root_dir = os.path.abspath(
    os.environ.get(
        "HPCS_ROOT_DIR",
        os.environ.get("PROJECT", os.environ.get("SCRATCH", os.environ.get("HOME", "/tmp"))),
    )
)

APPS_ROOT_DIR = os.path.abspath(os.environ.get("HPCS_APPS_ROOT_DIR", default_root_dir))
SCRIPTS_ROOT_DIR = os.path.abspath(os.environ.get("HPCS_SCRIPTS_ROOT_DIR", default_root_dir))
