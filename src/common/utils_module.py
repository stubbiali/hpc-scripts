# -*- coding: utf-8 -*-
from __future__ import annotations

import utils


def module_purge(force: bool = False) -> None:
    utils.run(f"module{' --force ' if force else ' '}purge")


def module_reset() -> None:
    utils.run("module reset")


def module_load(*module_names: str) -> None:
    for module_name in module_names:
        utils.run(f"module load {module_name}")
