#!/bin/bash -l

NUM_NODES=${NUM_NODES:-1}
TIME=${TIME:-01:00:00}

salloc \
  --account=p200061 \
  --res=gpudev \
  --qos=dev \
  --nodes="$NUM_NODES" \
  --time="$TIME"
