#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing .env file at ${ENV_FILE}" >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

: "${PULUMI_BUCKET_NAME:?PULUMI_BUCKET_NAME must be set in .env}"

aws --profile rustfs \
  --endpoint-url http://localhost:9000 \
  s3 mb s3://${PULUMI_BUCKET_NAME}

aws --profile rustfs \
  --endpoint-url http://localhost:9000 \
  s3 ls s3://
