#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import os
import typing

import defs
import generate_prepare_pmapl
import utils


# >>> config: start
BRANCH: str = "main"
COPY_GT_CACHE_TO_DEV_SHM: bool = False
COPY_GT_CACHE_TO_TMP: bool = False
ENABLE_CPROFILE: bool = False
ENV: defs.ProgrammingEnvironment = "gnu"
GHEX_AGGREGATE_FIELDS: bool = False
GHEX_COLLECT_STATISTICS: bool = False
GHEX_TRANSPORT_BACKEND: defs.GHEXTransportBackend = "mpi"
GT_BACKEND: str = "dace:gpu"
NUM_NODES: int = 1
NUM_RUNS: int = 1
NUM_TASKS_PER_NODE: int = 1
NUM_THREADS_PER_TASK: int = 1
OUTPUT_DIR: typing.Optional[str] = None
PARTITION: defs.Partition = "gpu"
PMAP_DISABLE_LOG: bool = False
PMAP_ENABLE_BENCHMARKING: bool = False
PMAP_ENABLE_OVERCOMPUTING: bool = False
PMAP_EXTENDED_TIMERS: bool = False
PMAP_PRECISION: defs.FloatingPointPrecision = "double"
ROOT_DIR: typing.Optional[str] = None
USE_CASE: str = "thermal"
# >>> config: end


def core(
    branch: str,
    copy_gt_cache_to_dev_shm: bool,
    copy_gt_cache_to_tmp: bool,
    enable_cprofile: bool,
    env: defs.ProgrammingEnvironment,
    ghex_aggregate_fields: bool,
    ghex_collect_statistics: bool,
    ghex_transport_backend: defs.GHEXTransportBackend,
    gt_backend: str,
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
    root_dir: typing.Optional[str],
    use_case: str,
) -> str:
    prepare_pmapl_fname, gt_cache_root = generate_prepare_pmapl.core(
        branch, env, ghex_transport_backend, partition, root_dir
    )

    with utils.batch_file(filename="run_pmapl") as (f, fname):
        utils.run(f". {prepare_pmapl_fname}")

        with utils.chdir("$PMAPL"):
            with utils.chdir("drivers"):
                utils.export_variable("GHEX_AGGREGATE_FIELDS", int(ghex_aggregate_fields))
                utils.export_variable("GHEX_COLLECT_STATISTICS", int(ghex_collect_statistics))
                utils.export_variable("GHEX_TRANSPORT_BACKEND", ghex_transport_backend.upper())
                utils.export_variable("GT_BACKEND", gt_backend)
                utils.export_variable("OMP_NUM_THREADS", num_threads_per_task)
                utils.export_variable("OMP_PLACES", "cores")
                utils.export_variable("OMP_PROC_BIND", "close")
                utils.export_variable("FVM_DISABLE_LOG", int(pmap_disable_log))
                utils.export_variable("FVM_ENABLE_BENCHMARKING", int(pmap_enable_benchmarking))
                utils.export_variable("FVM_ENABLE_OVERCOMPUTING", int(pmap_enable_overcomputing))
                utils.export_variable("FVM_EXTENDED_TIMERS", int(pmap_extended_timers))
                utils.export_variable("FVM_PRECISION", pmap_precision)
                # utils.export_variable("CUDA_LAUNCH_BLOCKING", 1)

                gt_backend_str = gt_backend.replace(":", "")

                if copy_gt_cache_to_dev_shm and copy_gt_cache_to_tmp:
                    raise RuntimeError("gtcache can be copied either to /dev/shm or to /tmp.")
                if copy_gt_cache_to_dev_shm:
                    dest = "/dev/shm"
                elif copy_gt_cache_to_tmp:
                    dest = "/tmp"
                else:
                    dest = None

                if dest is not None:
                    gt_cache_backend_dir = os.path.join(
                        gt_cache_root, f".gt_cache/py39_1013/{gt_backend_str}"
                    )
                    gt_cache_backend_tar = os.path.join(
                        gt_cache_root, f".gt_cache/py39_1013/{gt_backend_str}.tar"
                    )
                    if not os.path.exists(gt_cache_backend_tar):
                        utils.run(f"tar cf {gt_cache_backend_tar} {gt_cache_backend_dir}")

                    new_gt_cache_root = dest + gt_cache_root
                    utils.run(f"srun rm -rf {new_gt_cache_root}")
                    utils.run(f"srun mkdir -p {new_gt_cache_root}/.gt_cache/py39_1013")
                    utils.run(
                        f"srun tar xf {gt_cache_backend_tar} "
                        f"-C {new_gt_cache_root}/.gt_cache/py39_1013"
                    )
                    utils.export_variable("GT_CACHE_ROOT", new_gt_cache_root)

                if output_dir is not None:
                    output_dir = os.path.abspath(output_dir)
                else:
                    output_dir = os.path.join("$PWD", use_case, pmap_precision, gt_backend_str)
                utils.run(f"mkdir -p {output_dir}")

                command = (
                    f"CC=cc CXX=CC "
                    f"{'CUDA_HOST_CXX=CC' if gt_backend in ('dace:gpu', 'gt:gpu') else ''} "
                    f"srun --nodes={num_nodes} --ntasks-per-node={num_tasks_per_node} --unbuffered "
                    "python "
                )
                if enable_cprofile:
                    command += f"-m cProfile -o {output_dir}/profile_data_$(hostname).prof "
                command += (
                    f"run_model.py {os.path.join('../config', use_case + '.yml')} "
                    f"--output-directory={output_dir}"
                )
                if pmap_disable_log or pmap_enable_benchmarking:
                    command += " --write-profiling-data"

                for _ in range(num_runs):
                    utils.run(command)

                if dest is not None:
                    utils.run(f"srun rm -rf {new_gt_cache_root}")

    return fname


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--copy-gt-cache-to-dev-shm", type=bool, default=COPY_GT_CACHE_TO_DEV_SHM)
    parser.add_argument("--copy-gt-cache-to-tmp", type=bool, default=COPY_GT_CACHE_TO_TMP)
    parser.add_argument("--enable-cprofile", type=bool, default=ENABLE_CPROFILE)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--ghex-aggregate-fields", type=bool, default=GHEX_AGGREGATE_FIELDS)
    parser.add_argument("--ghex-collect-statistics", type=bool, default=GHEX_COLLECT_STATISTICS)
    parser.add_argument("--ghex-transport-backend", type=str, default=GHEX_TRANSPORT_BACKEND)
    parser.add_argument("--gt-backend", type=str, default=GT_BACKEND)
    parser.add_argument("--num-nodes", type=int, default=NUM_NODES)
    parser.add_argument("--num-runs", type=int, default=NUM_RUNS)
    parser.add_argument("--num-tasks-per-node", type=int, default=NUM_TASKS_PER_NODE)
    parser.add_argument("--num-threads-per-task", type=int, default=NUM_THREADS_PER_TASK)
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR)
    parser.add_argument("--partition", type=str, default=PARTITION)
    parser.add_argument("--pmap-disable-log", type=bool, default=PMAP_DISABLE_LOG)
    parser.add_argument("--pmap-enable-benchmarking", type=bool, default=PMAP_ENABLE_BENCHMARKING)
    parser.add_argument("--pmap-enable-overcomputing", type=bool, default=PMAP_ENABLE_OVERCOMPUTING)
    parser.add_argument("--pmap-extended-timers", type=bool, default=PMAP_EXTENDED_TIMERS)
    parser.add_argument("--pmap-precision", type=str, default=PMAP_PRECISION)
    parser.add_argument("--root-dir", type=str, default=ROOT_DIR)
    parser.add_argument("--use-case", type=str, default=USE_CASE)
    args = parser.parse_args()
    with utils.batch_directory():
        core(**args.__dict__)
