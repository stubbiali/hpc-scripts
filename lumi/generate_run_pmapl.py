#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import defs
import generate_prepare_pmapl
import utils


# >>> config: start
BRANCH: str = "coupling-refactoring"
COMPILER_VERSION: str = "16.0.1"
DEFAULT_BLOCK_SIZE: str = ""
ENV: defs.ProgrammingEnvironment = "cray"
ENV_VERSION: str = "8.4.0"
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GT_BACKEND: str = "gt:gpu"
HDF5_VERSION: str = "1.14.4.3"
NETCDF_VERSION: str = "4.9.2"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
PARTITION_TYPE: defs.PartitionType = "gpu"
PMAP_ENABLE_BENCHMARKING: bool = False
PMAP_ENABLE_OVERCOMPUTING: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
STACK: defs.SoftwareStack = "lumi"
STACK_VERSION: str = "23.09"
USE_CASE: str = "thermal"
# >>> config: end


def core(
    branch: str,
    compiler_version: str,
    default_block_size: str,
    env: defs.ProgrammingEnvironment,
    env_version: str,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    gt_backend: str,
    hdf5_version: str,
    netcdf_version: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    partition_type: defs.PartitionType,
    pmap_enable_benchmarking: bool,
    pmap_enable_overcomputing: bool,
    pmap_precision: defs.FloatingPointPrecision,
    stack: defs.SoftwareStack,
    stack_version: str,
    use_case: str,
) -> str:
    prepare_pmapl_fname, compiler = generate_prepare_pmapl.core(
        branch,
        compiler_version,
        env,
        env_version,
        hdf5_version,
        netcdf_version,
        partition_type,
        stack,
        stack_version,
    )

    with utils.batch_file(prefix="run_pmapl") as (f, fname):
        utils.run(f". {prepare_pmapl_fname}")

        with utils.chdir("$PMAPL"):
            utils.run(f". $PMAPL_VENV/bin/activate")
            with utils.chdir("drivers"):
                utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
                utils.export_variable("GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics))
                utils.export_variable("GT_BACKEND", gt_backend)
                utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                utils.export_variable("OMP_PLACES", "cores")
                utils.export_variable("OMP_PROC_BIND", "close")
                # utils.export_variable("OMP_DISPLAY_AFFINITY", "True")
                utils.export_variable("FVM_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking))
                utils.export_variable("FVM_ENABLE_OVERCOMPUTING", int(pmap_enable_overcomputing))
                utils.export_variable("FVM_PRECISION", pmap_precision)
                utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=4096'")
                if partition_type == "gpu":
                    utils.export_variable("DACE_DEFAULT_BLOCK_SIZE", default_block_size)

                srun_options = utils.get_srun_options(
                    num_nodes,
                    num_tasks_per_node,
                    num_threads_per_task,
                    partition_type,
                    gt_backend=gt_backend,
                )
                output_directory = os.path.join(
                    "$PWD",
                    use_case,
                    pmap_precision,
                    gt_backend.replace(":", "")
                )
                utils.run(f"mkdir -p {output_directory}")
                command = (
                    f"CC=cc CXX=CC "
                    f"srun {' '.join(srun_options)} ./../../../select_gpu.sh python run_model.py "
                    f"{os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_directory}"
                )
                if pmap_enable_benchmarking:
                    command += f" --write-profiling-data"

                for _ in range(num_runs):
                    utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--default-block-size", type=str, default=DEFAULT_BLOCK_SIZE)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--env-version", type=str, default=ENV_VERSION)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--hdf5-version", type=str, default=HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=NETCDF_VERSION)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-enable-overcomputing", type=bool, default=PMAP_ENABLE_OVERCOMPUTING)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with utils.batch_directory():
        core(**args.__dict__)
