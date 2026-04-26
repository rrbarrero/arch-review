#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"
INFRA_DIR="${REPO_ROOT}/infra"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing .env file at ${ENV_FILE}" >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

: "${PULUMI_BUCKET_NAME:?PULUMI_BUCKET_NAME must be set in .env}"
: "${PULUMI_BACKEND_ENDPOINT:?PULUMI_BACKEND_ENDPOINT must be set in .env}"
: "${PULUMI_PROJECT_NAME:?PULUMI_PROJECT_NAME must be set in .env}"
: "${PULUMI_STACK_NAME:?PULUMI_STACK_NAME must be set in .env}"
: "${PULUMI_CONFIG_PASSPHRASE:?PULUMI_CONFIG_PASSPHRASE must be set in .env}"
: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID must be set in .env}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY must be set in .env}"
: "${AWS_REGION:?AWS_REGION must be set in .env}"

PULUMI_BACKEND_URL="${PULUMI_BACKEND_URL:-s3://${PULUMI_BUCKET_NAME}?endpoint=${PULUMI_BACKEND_ENDPOINT}&disableSSL=true&s3ForcePathStyle=true}"

mkdir -p "${INFRA_DIR}"

echo "Logging into Pulumi backend ${PULUMI_BACKEND_URL}"
pulumi login "${PULUMI_BACKEND_URL}" --non-interactive

if [[ ! -f "${INFRA_DIR}/Pulumi.yaml" ]]; then
  echo "Initializing Pulumi project '${PULUMI_PROJECT_NAME}' in ${INFRA_DIR}"
  pulumi new python \
    --cwd "${INFRA_DIR}" \
    --name "${PULUMI_PROJECT_NAME}" \
    --stack "${PULUMI_STACK_NAME}" \
    --description "Infrastructure for ${PULUMI_PROJECT_NAME}" \
    --yes \
    --non-interactive
else
  echo "Pulumi project already exists in ${INFRA_DIR}. Skipping project initialization."
fi

if pulumi stack select "${PULUMI_STACK_NAME}" --cwd "${INFRA_DIR}" --non-interactive >/dev/null 2>&1; then
  echo "Pulumi stack '${PULUMI_STACK_NAME}' already exists and is selected."
else
  echo "Creating Pulumi stack '${PULUMI_STACK_NAME}'"
  pulumi stack init "${PULUMI_STACK_NAME}" --cwd "${INFRA_DIR}" --non-interactive
fi
