# -*- coding: utf-8 -*-
from __future__ import annotations

import common.utils
import common.utils_module
import defs


def module_load_compiler(compiler: defs.Compiler) -> None:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        if compiler == "gcc@11.2.0":
            common.utils_module.module_load("gcc/11.2.0-gcc-11.2.0")
            common.utils.export_variable("CC", "$(which gcc)")
            common.utils.export_variable("CXX", "$(which g++)")
            common.utils.export_variable("FC", "$(which gfortran)")
        elif "nvhpc" in compiler:
            common.utils_module.module_load("gcc/11.2.0-gcc-11.2.0")
            common.utils_module.module_load(f"{compiler.replace('@', '/')}-gcc-11.2.0")
            common.utils.export_variable(
                "CFLAGS", "'-noswitcherror --diag_suppress inline_gnu_noinline_conflict'"
            )
            common.utils.export_variable(
                "CPPFLAGS", "'-noswitcherror --diag_suppress inline_gnu_noinline_conflict'"
            )


def module_load_mpi(compiler: defs.Compiler, mpi: defs.MPI) -> None:
    with common.utils.check_argument("compiler", compiler, defs.valid_compilers):
        with common.utils.check_argument("mpi", mpi, defs.valid_mpi):
            assert mpi in defs.compilers_to_mpi_libraries[compiler]

            if mpi == "openmpi@4.1.2":
                if compiler == "gcc@11.2.0":
                    common.utils_module.module_load("openmpi/4.1.2-gcc-11.2.0")
            elif mpi == "openmpi@4.1.5":
                if compiler == "nvhpc@24.7":
                    common.utils_module.module_load("openmpi/4.1.5-nvhpc-24.7")
            elif mpi == "openmpi@4.1.6":
                if compiler == "nvhpc@23.9":
                    common.utils_module.module_load("openmpi/4.1.6-nvhpc-23.9")

            if "openmpi" in mpi:
                common.utils.export_variable("CC", "$(which mpicc)")
                common.utils.export_variable("CXX", "$(which mpiCC)")
                common.utils.export_variable("MPICC", "$(which mpicc)")
                common.utils.export_variable("MPICXX", "$(which mpiCC)")
