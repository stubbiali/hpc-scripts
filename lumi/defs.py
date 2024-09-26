# -*- coding: utf-8 -*-
import typing


FloatingPointPrecision = typing.Literal["double", "single"]
GHEXTransportBackend = typing.Literal["libfabric", "mpi", "ucx"]
Partition = typing.Literal["dev-g", "standard", "standard-g"]
PartitionType: dict[str, str] = {"dev-g": "gpu", "standard": "host", "standard-g": "gpu"}
ProgrammingEnvironment = typing.Literal["amd", "aocc", "cray", "gnu"]
SoftwareStack = typing.Literal["cray", "lumi"]

valid_ghex_transport_backends = typing.get_args(GHEXTransportBackend)
valid_programming_environments = typing.get_args(ProgrammingEnvironment)
valid_partitions = typing.get_args(Partition)
valid_partition_types = set(PartitionType.values())
valid_software_stacks = typing.get_args(SoftwareStack)
