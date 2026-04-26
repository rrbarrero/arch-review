.PHONY: provision kind-create kind-delete kind-status


KIND_CLUSTER_NAME ?= arch-review
KIND_CONFIG ?= ops/kind-config.yml
APP_IMAGE_NAME ?= arch-review-image
APP_IMAGE_TAG ?= dev
APP_IMAGE ?= $(APP_IMAGE_NAME):$(APP_IMAGE_TAG)

kind-create:
	kind create cluster --name $(KIND_CLUSTER_NAME) --config $(KIND_CONFIG)

kind-delete:
	kind delete cluster --name $(KIND_CLUSTER_NAME)

kind-status:
	kind get clusters

provision: kind-create
	cd ops && ./s3_bucket_provision.sh
