.PHONY: provision kind-create kind-delete kind-status s3-bucket pulumi-dev-stack check-env

ENV_FILE ?= .env

ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
endif

APP_IMAGE ?= $(APP_IMAGE_NAME):$(APP_IMAGE_TAG)

export KIND_CLUSTER_NAME KIND_CONFIG APP_IMAGE_NAME APP_IMAGE_TAG APP_IMAGE
export PULUMI_BUCKET_NAME PULUMI_BACKEND_ENDPOINT PULUMI_PROJECT_NAME PULUMI_STACK_NAME PULUMI_CONFIG_PASSPHRASE
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_REGION

check-env:
	@test -f $(ENV_FILE) || (echo "Missing $(ENV_FILE). Copy env.example to $(ENV_FILE)." >&2; exit 1)

kind-create: check-env
	./ops/kind_cluster_provision.sh

kind-delete: check-env
	kind delete cluster --name $(KIND_CLUSTER_NAME)

kind-status:
	kind get clusters

s3-bucket: check-env
	cd ops && ./s3_bucket_provision.sh

pulumi-dev-stack: check-env
	./ops/pulumi_dev_stack_provision.sh

provision: kind-create s3-bucket pulumi-dev-stack
