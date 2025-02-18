#!/sw/spack-levante/mambaforge-22.9.0-2-Linux-x86_64-kptncg/bin/python
# -*- coding: utf-8 -*-
import common.utils
import sbatch_pmap_les


# >>> config: start
ARGS = {
    "account": "bd1069",
    "branch": "main",
    "compiler": "nvhpc@24.7",
    "dace_default_block_size": None,
    "dry_run": False,
    "ghex_aggregate_fields": False,
    "ghex_collect_statistics": False,
    "ghex_transport_backend": "MPI",
    "gt_backend_list": ["dace:gpu"],
    "job_root_dir": "_jobs",
    "mpi": "openmpi@4.1.5",
    "num_runs": 1,
    "partition": "gpu",
    "pmap_disable_log": False,
    "pmap_enable_benchmarking": True,
    "pmap_extended_timers": False,
    "pmap_precision_list": ["double"],
    "python": "python@3.11",
    "reservation": None,
    "time": "01:00:00",
    "use_case_dict": {
        "weak-scaling/baroclinic-wave-sphere-moist/1": [common.utils.ThreadsLayout(1, 1, 1)]
        # "weak-scaling/baroclinic-wave-sphere-moist/16": [common.utils.ThreadsLayout(4, 4, 1)]
    },
}
# >>> config: end


if __name__ == "__main__":
    sbatch_pmap_les.core(**ARGS, project_name="pmap-les-dlr")
