# -*- coding: utf-8 -*-
import common
import defs


def spack_activate_pmap_env() -> None:
    common.utils.run(f"source {defs.spack_pmap_root}/share/spack/setup-env.sh")
    common.utils.run(f"spack env activate {defs.spack_pmap_env}")


def spack_activate_ecrad_env(python_version: defs.PythonVersion) -> None:
    common.utils.run(
        f"source {defs.scratch_dir}/ecrad-porting/_spack/c4449cb201/share/spack/setup-env.sh"
    )
    common.utils.run(
        f"spack env activate {defs.scratch_dir}/ecrad-porting/_spack/c4449cb201/_env/"
        f"py{python_version.replace('.', '')}"
    )


def load_python(version: defs.PythonVersion) -> str:
    with common.utils.check_argument("version", version, defs.valid_python_versions):
        if version == "3.10":
            common.utils_spack.spack_load("python@3.10")
            return "python"
        elif version == "3.11":
            common.utils_spack.spack_load("python@3.11")
            return "python"
        elif version == "3.12":
            return "py312"
