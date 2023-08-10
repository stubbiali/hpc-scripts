# -*- coding: utf-8 -*-
import typing

FloatingPointPrecision = typing.Literal["double", "single"]
PartitionType = typing.Literal["gpu", "host"]
ProgrammingEnvironment = typing.Literal["amd", "cray", "gnu"]
SoftwareStack = typing.Literal["cray", "lumi"]

valid_programming_environments = typing.get_args(ProgrammingEnvironment)
valid_partition_types = typing.get_args(PartitionType)
valid_software_stacks = typing.get_args(SoftwareStack)
