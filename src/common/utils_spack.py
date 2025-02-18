# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import TYPE_CHECKING

import utils

if TYPE_CHECKING:
    from typing import Optional


def spack_install(spec: str, compiler: str, dependencies: Optional[list[str]] = None) -> None:
    command = f"spack install {spec} %{compiler}"
    dependencies = dependencies or []
    for dependency in dependencies:
        command += f" ^{dependency}"  # %{compiler}"
    utils.run(command)


def spack_load(spec: str, compiler: str, dependencies: Optional[list[str]] = None) -> None:
    command = f"spack load {spec} %{compiler}"
    dependencies = dependencies or []
    for dependency in dependencies:
        command += f" ^{dependency} %{compiler}"
    utils.run(command)


def spack_unload() -> None:
    utils.run(f"spack unload --all")
