#!/bin/bash -l

ACCOUNT=${ACCOUNT:-p200177}
NUM_NODES=${NUM_NODES:-1}
TIME=${TIME:-01:00:00}

salloc \
  --account=p200177 \
  --res=gpudev \
  --qos=dev \
  --nodes="$NUM_NODES" \
  --time="$TIME" \
  -vvv
