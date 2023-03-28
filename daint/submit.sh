#!/bin/bash -l

ACCOUNT=${ACCOUNT:-s299}
JOB_NAME=${JOB_NAME:-test_job}
JOB_SCRIPT=${JOB_SCRIPT:-run_fvm.sh}
NUM_NODES=${NUM_NODES:-1}
TIME=${TIME:-01:00:00}

sbatch \
	--account="$ACCOUNT" \
	--constraint=gpu \
	--distribution=block \
	--error=error/"${JOB_NAME}".err \
	--exclusive \
	--job-name="${JOB_NAME}" \
	--nodes="${NUM_NODES}" \
	--output=output/"${JOB_NAME}".out \
	--partition=normal \
	--time="${TIME}" \
	"${JOB_SCRIPT}"
#--contiguous \
