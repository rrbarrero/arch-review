from typing import Sequence

import pulumi
import pulumi_kubernetes as k8s

from common import labels, namespaced_metadata, related_name, secret_key_ref
from settings import Settings


def create_namespace(settings: Settings) -> pulumi.Output[str]:
    namespace = k8s.core.v1.Namespace(
        "app-namespace",
        metadata={
            "name": settings.namespace,
        },
    )
    return namespace.metadata["name"]


def create_app(
    settings: Settings,
    namespace_name: pulumi.Input[str],
    dependencies: Sequence[pulumi.Resource] | None = None,
) -> k8s.core.v1.Service:
    app_labels = labels(settings.app_name)
    pgvector_secret_name = related_name(settings.pgvector_name, "secret")
    neo4j_secret_name = related_name(settings.neo4j_name, "secret")

    k8s.apps.v1.Deployment(
        settings.app_name,
        metadata=namespaced_metadata(namespace_name, settings.app_name),
        spec={
            "selector": {
                "matchLabels": app_labels,
            },
            "replicas": settings.replicas,
            "template": {
                "metadata": {
                    "labels": app_labels,
                },
                "spec": {
                    "containers": [
                        {
                            "name": settings.app_name,
                            "image": settings.image,
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "containerPort": settings.app_port,
                                }
                            ],
                            "env": [
                                {
                                    "name": "PGVECTOR_HOST",
                                    "value": settings.pgvector_name,
                                },
                                {
                                    "name": "PGVECTOR_PORT",
                                    "value": str(settings.pgvector_port),
                                },
                                {
                                    "name": "PGVECTOR_DATABASE",
                                    "value": settings.pgvector_db,
                                },
                                {
                                    "name": "PGVECTOR_USER",
                                    "value": settings.pgvector_user,
                                },
                                {
                                    "name": "PGVECTOR_PASSWORD",
                                    "valueFrom": secret_key_ref(
                                        pgvector_secret_name,
                                        "POSTGRES_PASSWORD",
                                    ),
                                },
                                {
                                    "name": "NEO4J_URI",
                                    "value": (
                                        f"bolt://{settings.neo4j_name}:"
                                        f"{settings.neo4j_bolt_port}"
                                    ),
                                },
                                {
                                    "name": "NEO4J_USER",
                                    "value": settings.neo4j_user,
                                },
                                {
                                    "name": "NEO4J_PASSWORD",
                                    "valueFrom": secret_key_ref(
                                        neo4j_secret_name,
                                        "NEO4J_PASSWORD",
                                    ),
                                },
                                {
                                    "name": "CORS_ORIGINS_RAW",
                                    "value": pulumi.Output.concat(
                                        "http://",
                                        settings.ingress_host,
                                        ":",
                                        str(settings.traefik_http_node_port),
                                    ),
                                },
                                {
                                    "name": "OLLAMA_BASE_URL",
                                    "value": settings.ollama_base_url,
                                },
                                {
                                    "name": "LLM_MODEL",
                                    "value": settings.llm_model,
                                },
                                {
                                    "name": "LLM_TEMPERATURE",
                                    "value": str(settings.llm_temperature),
                                },
                                {
                                    "name": "EMBEDDING_MODEL",
                                    "value": settings.embedding_model,
                                },
                                {
                                    "name": "OTEL_EXPORTER_OTLP_ENDPOINT",
                                    "value": pulumi.Output.concat(
                                        "http://", settings.tempo_name, ":",
                                        str(settings.tempo_otlp_grpc_port),
                                    ),
                                },
                                {
                                    "name": "OTEL_SERVICE_NAME",
                                    "value": "arch-review",
                                },
                            ],
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": settings.app_port,
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 10,
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": settings.app_port,
                                },
                                "initialDelaySeconds": 15,
                                "periodSeconds": 20,
                            },
                        }
                    ],
                },
            },
        },
        opts=pulumi.ResourceOptions(depends_on=dependencies or []),
    )

    return k8s.core.v1.Service(
        settings.app_name,
        metadata=namespaced_metadata(namespace_name, settings.app_name),
        spec={
            "selector": app_labels,
            "ports": [
                {
                    "port": settings.app_port,
                    "targetPort": settings.app_port,
                }
            ],
        },
    )


def create_ingress(
    settings: Settings,
    namespace_name: pulumi.Input[str],
    dependencies: Sequence[pulumi.Resource],
) -> None:
    k8s.networking.v1.Ingress(
        settings.app_name,
        metadata={
            **namespaced_metadata(namespace_name, settings.app_name),
            "annotations": {
                "pulumi.com/skipAwait": "true",
            },
        },
        spec={
            "ingressClassName": settings.traefik_ingress_class,
            "rules": [
                {
                    "host": settings.ingress_host,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": settings.app_name,
                                        "port": {
                                            "number": settings.app_port,
                                        },
                                    }
                                },
                            }
                        ]
                    },
                }
            ],
        },
        opts=pulumi.ResourceOptions(depends_on=dependencies),
    )
