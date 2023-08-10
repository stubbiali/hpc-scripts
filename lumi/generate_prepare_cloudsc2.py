#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import defs
import generate_prepare_cloudsc


# >>> config: start
BRANCH: str = "gt4py"
ENV: defs.ProgrammingEnvironment = "cray"
PARTITION_TYPE: defs.PartitionType = "gpu"
STACK: defs.SoftwareStack = "lumi"
# >>> config: end


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=ENV)
    parser.add_argument("--partition-type", type=str, default=PARTITION_TYPE)
    parser.add_argument("--stack", type=str, default=STACK)
    args = parser.parse_args()
    generate_prepare_cloudsc.core(**args.__dict__, project="cloudsc2")
