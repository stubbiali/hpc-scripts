# -*- coding: utf-8 -*-
from typing import Literal, get_args


FloatingPointPrecision = Literal["double", "single"]
GHEXTransportBackend = Literal["libfabric", "mpi", "ucx"]
Partition = Literal["dev-g", "small-g", "standard", "standard-g"]
PartitionType: dict[Partition, Literal["gpu", "host"]] = {
    "dev-g": "gpu",
    "small-g": "gpu",
    "standard": "host",
    "standard-g": "gpu",
}
ProgrammingEnvironment = Literal["amd", "aocc", "cray", "gnu"]
SoftwareStack = Literal["cray", "lumi"]

valid_ghex_transport_backends = get_args(GHEXTransportBackend)
valid_programming_environments = get_args(ProgrammingEnvironment)
valid_partitions = get_args(Partition)
valid_partition_types = set(PartitionType.values())
valid_software_stacks = get_args(SoftwareStack)
