#!/opt/cray/pe/python/3.9.12.1/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import utils


def core():
    utils.run("rm -rf _error/*")
    utils.run("rm -rf _output/*")
    utils.run("rm -rf _tmp/*")


if __name__ == "__main__":
    core()
