#!/bin/bash

ACCOUNT=${ACCOUNT:-s299}
NUM_NODES=${NUM_NODES:-1}
TIME=${TIME:-01:00:00}

# srun --pty --x11 --account=s299m --constraint=mc --partition=normal --time=04:00:00 bash
# srun --pty --account=s299 --constraint=gpu --partition=normal --time=02:00:00 bash
salloc \
  --account="$ACCOUNT" \
  --constraint=gpu \
  --nodes="$NUM_NODES" \
  --partition=normal \
  --time="$TIME"
