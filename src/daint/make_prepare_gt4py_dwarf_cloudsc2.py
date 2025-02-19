#!/opt/python/3.9.4.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse

import defaults
from make_prepare_gt4py_dwarf_cloudsc import core


# >>> config: start
BRANCH: str = "main"
# >>> config: end


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=str, default=BRANCH)
    parser.add_argument("--env", type=str, default=defaults.ENV)
    parser.add_argument("--partition", type=str, default=defaults.PARTITION)
    args = parser.parse_args()
    core(**args.__dict__, project="gt4py-dwarf-p-cloudsc2-tl-ad")
