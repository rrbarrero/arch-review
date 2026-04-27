.PHONY: install env-init check-tools compose-infra provision kind-create kind-delete kind-status s3-bucket pulumi-dev-stack infra-deps pulumi-preview pulumi-up app-image-build app-image-load app-image-push app-deploy frontend-image-build frontend-image-load frontend-image-push frontend-deploy check-env dev test ruff ty lint uv-add-dev

ENV_FILE ?= .env

ifneq (,$(wildcard $(ENV_FILE)))
include $(ENV_FILE)
endif

APP_IMAGE ?= $(APP_IMAGE_NAME):$(APP_IMAGE_TAG)
FRONTEND_IMAGE ?= $(FRONTEND_IMAGE_NAME):$(FRONTEND_IMAGE_TAG)

export KIND_CLUSTER_NAME KIND_CONFIG APP_IMAGE_NAME APP_IMAGE_TAG APP_IMAGE
export FRONTEND_IMAGE_NAME FRONTEND_IMAGE_TAG FRONTEND_IMAGE
export PULUMI_BUCKET_NAME PULUMI_BACKEND_ENDPOINT PULUMI_PROJECT_NAME PULUMI_STACK_NAME PULUMI_CONFIG_PASSPHRASE
export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_REGION

install: env-init check-tools
	$(MAKE) compose-infra provision deploy

env-init:
	@test -f $(ENV_FILE) || cp env.example $(ENV_FILE)

check-tools:
	@command -v docker >/dev/null || (echo "Missing required command: docker" >&2; exit 1)
	@command -v kind >/dev/null || (echo "Missing required command: kind" >&2; exit 1)
	@command -v pulumi >/dev/null || (echo "Missing required command: pulumi" >&2; exit 1)
	@command -v aws >/dev/null || (echo "Missing required command: aws" >&2; exit 1)
	@command -v python >/dev/null || (echo "Missing required command: python" >&2; exit 1)

check-env:
	@test -f $(ENV_FILE) || (echo "Missing $(ENV_FILE). Copy env.example to $(ENV_FILE)." >&2; exit 1)

compose-infra: check-env
	docker compose up -d rustfs pgvector neo4j

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

infra-deps: pulumi-dev-stack
	test -d infra/venv || python -m venv infra/venv
	infra/venv/bin/python -m pip install -r infra/requirements.txt

provision: kind-create s3-bucket pulumi-dev-stack

app-image-build: check-env
	docker build -f app/Dockerfile -t $(APP_IMAGE) .

app-image-load: app-image-build
	kind load docker-image $(APP_IMAGE) --name $(KIND_CLUSTER_NAME)

app-image-push: app-image-load

frontend-image-build: check-env
	docker build -f frontend/Dockerfile -t $(FRONTEND_IMAGE) frontend

frontend-image-load: frontend-image-build
	kind load docker-image $(FRONTEND_IMAGE) --name $(KIND_CLUSTER_NAME)

frontend-image-push: frontend-image-load

pulumi-preview: infra-deps
	cd infra && pulumi preview --stack $(PULUMI_STACK_NAME)

pulumi-up: infra-deps
	cd infra && pulumi config set image $(APP_IMAGE) --stack $(PULUMI_STACK_NAME)
	cd infra && pulumi config set frontend_image $(FRONTEND_IMAGE) --stack $(PULUMI_STACK_NAME)
	cd infra && pulumi up --yes --stack $(PULUMI_STACK_NAME)

deploy: kind-create app-image-push frontend-image-push pulumi-up

dev: check-env
	docker compose up -d
	docker compose run --rm dbmate
	@echo "Backend:    http://localhost:8000"
	@echo "Frontend:   http://localhost:3000"
	@echo "Grafana:    http://localhost:3001"
	@echo "Prometheus: http://localhost:9090"
	@echo "Loki:       http://localhost:3100"

dbmate:
	docker compose run --rm dbmate

test:
	docker compose run --rm app uv run pytest tests/ -v

ruff:
	docker compose run --rm app uv run ruff check .

ty:
	docker compose run --rm app uv run ty check --exclude infra

lint: ruff ty

uv-add:
	docker compose run --rm app uv add $(pkg)

uv-add-dev:
	docker compose run --rm app uv add --dev $(pkg)
