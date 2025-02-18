# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib
import os
from typing import Literal

import common.utils
import defs


def core(
    branch: str,
    compiler: defs.Compiler,
    dace_default_block_size: str,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    ghex_transport_backend: defs.GHEXTransportBackend,
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
        branch, compiler, ghex_transport_backend, mpi, num_nodes, partition, python, project_name
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
                    f"srun {' '.join(srun_options)} python run_model.py "
                    f"{os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_dir}"
                )
                if pmap_enable_benchmarking:
                    command += f" --write-profiling-data"

                for _ in range(num_runs):
                    common.utils.run(command)

    return fname
