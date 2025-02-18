#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import importlib
import os
from typing import Literal

import common.utils
import defs
import defaults


# >>> config: start
BRANCH: str = "main"
DACE_DEFAULT_BLOCK_SIZE: str = ""
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GT_BACKEND: str = "gt:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = False
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
USE_CASE: str = "thermal"
# >>> config: end


def core(
    branch: str,
    compiler: defs.Compiler,
    dace_default_block_size: str,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    gt_backend: str,
    mpi: defs.MPI,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    output_dir: str,
    partition: defs.Partition,
    pmap_disable_log: bool,
    pmap_enable_benchmarking: bool,
    pmap_extended_timers: bool,
    pmap_precision: defs.FloatingPointPrecision,
    python: defs.Python,
    use_case: str,
    project_name: Literal["pmap-les", "pmap-les-dlr"],
) -> str:
    project_name_with_underscores = project_name.replace("-", "_")
    project_name_with_underscores_upper = project_name_with_underscores.upper()
    make_prepare_module = importlib.import_module(f"make_prepare_{project_name_with_underscores}")
    assert hasattr(make_prepare_module, "core")
    prepare_fname = make_prepare_module.core(
        branch, compiler, mpi, num_nodes, partition, python, project_name
    )

    with common.utils.batch_file(filename=f"run_{project_name_with_underscores}") as (f, fname):
        common.utils.run(f". {prepare_fname}")

        with common.utils.chdir(f"${project_name_with_underscores_upper}"):
            common.utils.run(f". ${project_name_with_underscores_upper}_VENV/bin/activate")
            with common.utils.chdir("drivers"):
                common.utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
                common.utils.export_variable(
                    "GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics)
                )
                common.utils.export_variable("GT_BACKEND", gt_backend)
                common.utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                common.utils.export_variable("OMP_PLACES", "cores")
                common.utils.export_variable("OMP_PROC_BIND", "close")
                # common.utils.export_variable("OMP_DISPLAY_AFFINITY", "True")
                common.utils.export_variable("FVM_DISABLE_LOG", int(pmap_disable_log))
                common.utils.export_variable(
                    "FVM_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking)
                )
                common.utils.export_variable("FVM_EXTENDED_TIMERS", int(pmap_extended_timers))
                common.utils.export_variable("FVM_PRECISION", pmap_precision)
                # common.utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=4096'")
                if partition == "gpu":
                    common.utils.export_variable("DACE_DEFAULT_BLOCK_SIZE", dace_default_block_size)

                if output_dir is not None:
                    output_dir = os.path.abspath(output_dir)
                else:
                    output_dir = os.path.join(
                        "$PWD", use_case, pmap_precision, gt_backend.replace(":", "")
                    )
                common.utils.run(f"mkdir -p {output_dir}")

                srun_options = [
                    f"--nodes={num_nodes}",
                    f"--ntasks-per-node={num_tasks_per_node}",
                    f"--cpus-per-task={num_threads_per_task}",
                ]
                if partition == "gpu":
                    srun_options.append("--gpus-per-task=1")
                command = (
                    f"CC=cc CXX=CC "
                    f"srun {' '.join(srun_options)} python run_model.py "
                    f"{os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_dir}"
                )
                if pmap_enable_benchmarking:
                    command += f" --write-profiling-data"

                for _ in range(num_runs):
                    common.utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler", type=str, default=defaults.COMPILER)
    parser.add_argument("--dace-default-block-size", type=str, default=DACE_DEFAULT_BLOCK_SIZE)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--pmap-disable-log", type=bool, default=PMAP_DISABLE_LOG)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-extended-timers", type=bool, default=PMAP_EXTENDED_TIMERS)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--python", type=str, default=defaults.PYTHON)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with common.utils.batch_directory():
        core(**args.__dict__, project_name="pmap-les")
