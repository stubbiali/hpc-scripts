#!/bin/bash -l

ACCOUNT=${ACCOUNT:-ecrdmonm}
JOB_NAME=${JOB_NAME:-test_job}
JOB_SCRIPT=${JOB_SCRIPT:-run_fvm.sh}
NUM_NODES=${NUM_NODES:-1}
NUM_TASKS=${NUM_TASKS:-1}
TIME=${TIME:-01:00:00}

sbatch \
	--account="$ACCOUNT" \
	--error=error/"$JOB_NAME".err \
  --export=ALL \
	--job-name="$JOB_NAME" \
	--nodes="$NUM_NODES" \
  --ntasks="$NUM_TASKS" \
	--output=output/"$JOB_NAME".out \
	--partition=par \
	--time="$TIME" \
	"$JOB_SCRIPT"
#--contiguous \
