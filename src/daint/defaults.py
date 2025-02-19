# -*- coding: utf-8 -*-
import defs

# project_id="$(sacct --format=Account --noheader | head -n 1 | awk '{$1=$1}1')"
# ACCOUNT: str = project_id
ACCOUNT: str = "s299"
ENV: defs.ProgrammingEnvironment = "gnu"
GHEX_TRANSPORT_BACKEND: defs.GHEXTransportBackend = "mpi"
PARTITION: defs.Partition = "gpu"
PRECISION: defs.FloatingPointPrecision = "double"
