#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os

import update_path

import common_utils
import defaults
import defs
import make_prepare_pmapl
import utils


# >>> config: start
BRANCH: str = "coupling-refactoring"
DEFAULT_BLOCK_SIZE: str = ""
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GT_BACKEND: str = "gt:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = False
PMAP_ENABLE_OVERCOMPUTING: bool = False
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
USE_CASE: str = "thermal"
# >>> config: end


def core(
    branch: str,
    default_block_size: str,
    env: defs.ProgrammingEnvironment,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    ghex_transport_backend: defs.GHEXTransportBackend,
    gt_backend: str,
    hdf5_version: str,
    netcdf_version: str,
    num_nodes: int,
    num_runs: int,
    num_tasks_per_node: int,
    num_threads_per_task: int,
    output_dir: str,
    partition: defs.Partition,
    pmap_disable_log: bool,
    pmap_enable_benchmarking: bool,
    pmap_enable_overcomputing: bool,
    pmap_extended_timers: bool,
    pmap_precision: defs.FloatingPointPrecision,
    rocm_version: str,
    stack: defs.SoftwareStack,
    stack_version: str,
    use_case: str,
) -> str:
    prepare_pmapl_fname = make_prepare_pmapl.core(
        branch,
        env,
        ghex_transport_backend,
        hdf5_version,
        netcdf_version,
        partition,
        rocm_version,
        stack,
        stack_version,
    )

    with common_utils.batch_file(filename="run_pmapl") as (f, fname):
        common_utils.run(f". {prepare_pmapl_fname}")

        with common_utils.chdir("$PMAPL"):
            common_utils.run(f". $PMAPL_VENV/bin/activate")
            with common_utils.chdir("drivers"):
                common_utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
                common_utils.export_variable(
                    "GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics)
                )
                common_utils.export_variable("GT_BACKEND", gt_backend)
                common_utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                common_utils.export_variable("OMP_PLACES", "cores")
                common_utils.export_variable("OMP_PROC_BIND", "close")
                # common_utils.export_variable("OMP_DISPLAY_AFFINITY", "True")
                common_utils.export_variable("FVM_DISABLE_LOG", int(pmap_disable_log))
                common_utils.export_variable(
                    "FVM_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking)
                )
                common_utils.export_variable(
                    "FVM_ENABLE_OVERCOMPUTING", int(pmap_enable_overcomputing)
                )
                common_utils.export_variable("FVM_EXTENDED_TIMERS", int(pmap_extended_timers))
                common_utils.export_variable("FVM_PRECISION", pmap_precision)
                common_utils.export_variable("GT4PY_EXTRA_COMPILE_ARGS", "'-fbracket-depth=4096'")
                if utils.get_partition_type(partition) == "gpu":
                    common_utils.export_variable("DACE_DEFAULT_BLOCK_SIZE", default_block_size)

                srun_options = utils.get_srun_options(
                    num_nodes,
                    num_tasks_per_node,
                    num_threads_per_task,
                    partition,
                    gt_backend=gt_backend,
                )
                if output_dir is not None:
                    output_dir = os.path.abspath(output_dir)
                else:
                    output_dir = os.path.join(
                        "$PWD", use_case, pmap_precision, gt_backend.replace(":", "")
                    )
                common_utils.run(f"mkdir -p {output_dir}")
                command = (
                    f"CC=cc CXX=CC "
                    f"srun {' '.join(srun_options)} ./../../../select_gpu.sh python run_model.py "
                    f"{os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_dir}"
                )
                if pmap_enable_benchmarking:
                    command += f" --write-profiling-data"

                for _ in range(num_runs):
                    common_utils.run(command)

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--default-block-size", type=str, default=DEFAULT_BLOCK_SIZE)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument(
        "--ghex-transport-backend", type=bool, default=defaults.GHEX_TRANSPORT_BACKEND
    )
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--hdf5-version", type=str, default=defaults.HDF5_VERSION)
    parser.add_argument("--netcdf-version", type=str, default=defaults.NETCDF_VERSION)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--pmap-disable-log", type=bool, default=PMAP_DISABLE_LOG)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-enable-overcomputing", type=bool, default=PMAP_ENABLE_OVERCOMPUTING)
    parser.add_argument("--pmap-extended-timers", type=bool, default=PMAP_EXTENDED_TIMERS)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--rocm-version", type=str, default=defaults.ROCM_VERSION)
    parser.add_argument("--stack", type=str, default=defaults.STACK)
    parser.add_argument("--stack-version", type=str, default=defaults.STACK_VERSION)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with common_utils.batch_directory():
        core(**args.__dict__)
