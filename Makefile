.PHONY: provision kind-create kind-delete kind-status check-env

ENV_FILE ?= .env

ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
endif

APP_IMAGE ?= $(APP_IMAGE_NAME):$(APP_IMAGE_TAG)

export KIND_CLUSTER_NAME KIND_CONFIG APP_IMAGE_NAME APP_IMAGE_TAG APP_IMAGE PULUMI_BUCKET_NAME

check-env:
	@test -f $(ENV_FILE) || (echo "Missing $(ENV_FILE). Copy env.example to $(ENV_FILE)." >&2; exit 1)

kind-create: check-env
	./ops/kind_cluster_provision.sh

kind-delete: check-env
	kind delete cluster --name $(KIND_CLUSTER_NAME)

kind-status:
	kind get clusters

provision: kind-create
	cd ops && ./s3_bucket_provision.sh
