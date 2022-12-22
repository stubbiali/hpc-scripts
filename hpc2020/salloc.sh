#!/bin/bash -l

NUM_NODES=${NUM_NODES:-1}
NUM_TASKS=${NUM_TASKS:-}
TIME=${TIME:-01:00:00}

if [ -z "$NUM_TASKS" ]; then
  NUM_TASKS="$NUM_NODES"
fi

salloc \
    --account=ecrdmonm \
    --cpus-per-task=256 \
    --partition=par \
    --qos=np \
    --nodes="$NUM_NODES" \
    --ntasks="$NUM_TASKS" \
    --sockets-per-node=2 \
    --time="$TIME"
