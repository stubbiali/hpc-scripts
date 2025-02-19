# -*- coding: utf-8 -*-
from typing import Literal, get_args

FloatingPointPrecision = Literal["double", "single"]
GHEXTransportBackend = Literal["libfabric", "mpi", "ucx"]
Partition = Literal["gpu", "mc"]
ProgrammingEnvironment = Literal["gnu"]

valid_programming_environments = get_args(ProgrammingEnvironment)
valid_partitions = get_args(Partition)
