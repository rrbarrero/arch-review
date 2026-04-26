#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

: "${KIND_CLUSTER_NAME:?KIND_CLUSTER_NAME must be set in .env}"
: "${KIND_CONFIG:?KIND_CONFIG must be set in .env}"

if [[ "${KIND_CONFIG}" != /* ]]; then
  KIND_CONFIG="${REPO_ROOT}/${KIND_CONFIG}"
fi

if kind get clusters | grep -Fxq "${KIND_CLUSTER_NAME}"; then
  echo "Kind cluster '${KIND_CLUSTER_NAME}' already exists. Skipping creation."
  exit 0
fi

kind create cluster --name "${KIND_CLUSTER_NAME}" --config "${KIND_CONFIG}"
