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
: "${PULUMI_BACKEND_ENDPOINT:?PULUMI_BACKEND_ENDPOINT must be set in .env}"
: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID must be set in .env}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY must be set in .env}"
: "${AWS_REGION:?AWS_REGION must be set in .env}"

S3_ENDPOINT_URL="http://${PULUMI_BACKEND_ENDPOINT}"

if aws --endpoint-url "${S3_ENDPOINT_URL}" s3 ls "s3://${PULUMI_BUCKET_NAME}" >/dev/null 2>&1; then
  echo "S3 bucket '${PULUMI_BUCKET_NAME}' already exists. Skipping creation."
else
  aws --endpoint-url "${S3_ENDPOINT_URL}" \
    s3 mb "s3://${PULUMI_BUCKET_NAME}"
fi

aws --endpoint-url "${S3_ENDPOINT_URL}" \
  s3 ls s3://
