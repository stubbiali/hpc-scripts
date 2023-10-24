# -*- coding: utf-8 -*-
import typing

FloatingPointPrecision = typing.Literal["double", "single"]
Partition = typing.Literal["gpu", "mc"]
ProgrammingEnvironment = typing.Literal["gnu"]

valid_programming_environments = typing.get_args(ProgrammingEnvironment)
valid_partitions = typing.get_args(Partition)
