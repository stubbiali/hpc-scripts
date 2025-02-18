#!/bin/bash -l

ACCOUNT=${ACCOUNT:-ecrdmonm}
NUM_NODES=${NUM_NODES:-1}
TIME=${TIME:-01:00:00}

salloc \
    --account="$ACCOUNT" \
    --partition=par \
    --qos=np \
    --nodes="$NUM_NODES" \
    --sockets-per-node=2 \
    --time="$TIME"
