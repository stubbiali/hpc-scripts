#!/opt/cray/pe/python/3.11.7/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import defaults
import make_prepare_cloudsc


# >>> config: start
BRANCH: str = "gt4py"
# >>> config: end


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    parser.add_argument("--rocm-version", type=str, default=defaults.ROCM_VERSION)
    parser.add_argument("--stack", type=str, default=STACK)
    parser.add_argument("--stack-version", type=str, default=STACK_VERSION)
    args = parser.parse_args()
    make_prepare_cloudsc.core(**args.__dict__, project="cloudsc2")
