#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from typing import Optional

import defs
import generate_prepare_cloudsc


# >>> config: start
BRANCH: str = "gt4py"
COMPILER_VERSION: str = "16.0.1"
ENV: defs.ProgrammingEnvironment = "cray"
ENV_VERSION: str = "8.4.0"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
STACK_VERSION: Optional[str] = "23.09"
# >>> config: end


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--compiler-version", type=str, default=COMPILER_VERSION)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--env-version", type=str, default=ENV_VERSION)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    args = parser.parse_args()
    generate_prepare_cloudsc.core(**args.__dict__, project="cloudsc2")
