# -*- coding: utf-8 -*-
from __future__ import annotations

import common.utils


def setup_cuda() -> None:
    # run("NVCC_PATH=$(which nvcc)")
    # run("CUDA_PATH=$(echo $NVCC_PATH | sed -e 's/\/bin\/nvcc//g')")
    common.utils.export_variable("CUDA_ROOT", "$CUDA_HOME")
    common.utils.export_variable("LD_LIBRARY_PATH", "$CUDA_HOME/lib64:$LD_LIBRARY_PATH")
