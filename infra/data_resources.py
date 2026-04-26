import pulumi_kubernetes as k8s

from common import labels, namespaced_metadata, related_name, secret_key_ref
from settings import Settings


def create_pgvector(
    settings: Settings,
    namespace_name,
) -> k8s.core.v1.Service:
    pgvector_labels = labels(settings.pgvector_name)
    pgvector_secret_name = related_name(settings.pgvector_name, "secret")
    pgvector_claim_name = related_name(settings.pgvector_name, "pvc")
    pgvector_volume_name = related_name(settings.pgvector_name, "data")

    k8s.core.v1.Secret(
        pgvector_secret_name,
        metadata=namespaced_metadata(namespace_name, pgvector_secret_name),
        string_data={
            "POSTGRES_PASSWORD": settings.pgvector_password,
        },
    )

    k8s.core.v1.PersistentVolumeClaim(
        pgvector_claim_name,
        metadata=namespaced_metadata(namespace_name, pgvector_claim_name),
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {
                "requests": {
                    "storage": settings.pgvector_storage_size,
                },
            },
        },
    )

    k8s.apps.v1.Deployment(
        settings.pgvector_name,
        metadata=namespaced_metadata(namespace_name, settings.pgvector_name),
        spec={
            "selector": {
                "matchLabels": pgvector_labels,
            },
            "replicas": 1,
            "template": {
                "metadata": {
                    "labels": pgvector_labels,
                },
                "spec": {
                    "containers": [
                        {
                            "name": settings.pgvector_name,
                            "image": settings.pgvector_image,
                            "ports": [
                                {
                                    "containerPort": settings.pgvector_port,
                                }
                            ],
                            "env": [
                                {
                                    "name": "POSTGRES_DB",
                                    "value": settings.pgvector_db,
                                },
                                {
                                    "name": "POSTGRES_USER",
                                    "value": settings.pgvector_user,
                                },
                                {
                                    "name": "POSTGRES_PASSWORD",
                                    "valueFrom": secret_key_ref(
                                        pgvector_secret_name,
                                        "POSTGRES_PASSWORD",
                                    ),
                                },
                            ],
                            "volumeMounts": [
                                {
                                    "name": pgvector_volume_name,
                                    "mountPath": "/var/lib/postgresql/data",
                                }
                            ],
                            "readinessProbe": {
                                "tcpSocket": {
                                    "port": settings.pgvector_port,
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10,
                            },
                        }
                    ],
                    "volumes": [
                        {
                            "name": pgvector_volume_name,
                            "persistentVolumeClaim": {
                                "claimName": pgvector_claim_name,
                            },
                        }
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        settings.pgvector_name,
        metadata=namespaced_metadata(namespace_name, settings.pgvector_name),
        spec={
            "selector": pgvector_labels,
            "ports": [
                {
                    "port": settings.pgvector_port,
                    "targetPort": settings.pgvector_port,
                }
            ],
        },
    )


def create_neo4j(
    settings: Settings,
    namespace_name,
) -> k8s.core.v1.Service:
    neo4j_labels = labels(settings.neo4j_name)
    neo4j_secret_name = related_name(settings.neo4j_name, "secret")
    neo4j_claim_name = related_name(settings.neo4j_name, "pvc")
    neo4j_volume_name = related_name(settings.neo4j_name, "data")

    k8s.core.v1.Secret(
        neo4j_secret_name,
        metadata=namespaced_metadata(namespace_name, neo4j_secret_name),
        string_data={
            "NEO4J_PASSWORD": settings.neo4j_password,
        },
    )

    k8s.core.v1.PersistentVolumeClaim(
        neo4j_claim_name,
        metadata=namespaced_metadata(namespace_name, neo4j_claim_name),
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {
                "requests": {
                    "storage": settings.neo4j_storage_size,
                },
            },
        },
    )

    k8s.apps.v1.Deployment(
        settings.neo4j_name,
        metadata=namespaced_metadata(namespace_name, settings.neo4j_name),
        spec={
            "selector": {
                "matchLabels": neo4j_labels,
            },
            "replicas": 1,
            "template": {
                "metadata": {
                    "labels": neo4j_labels,
                },
                "spec": {
                    "enableServiceLinks": False,
                    "containers": [
                        {
                            "name": settings.neo4j_name,
                            "image": settings.neo4j_image,
                            "ports": [
                                {
                                    "name": "http",
                                    "containerPort": settings.neo4j_http_port,
                                },
                                {
                                    "name": "bolt",
                                    "containerPort": settings.neo4j_bolt_port,
                                },
                            ],
                            "env": [
                                {
                                    "name": "NEO4J_AUTH",
                                    "value": settings.neo4j_password.apply(
                                        lambda password: (
                                            f"{settings.neo4j_user}/{password}"
                                        )
                                    ),
                                },
                            ],
                            "volumeMounts": [
                                {
                                    "name": neo4j_volume_name,
                                    "mountPath": "/data",
                                }
                            ],
                            "readinessProbe": {
                                "tcpSocket": {
                                    "port": settings.neo4j_bolt_port,
                                },
                                "initialDelaySeconds": 20,
                                "periodSeconds": 10,
                            },
                        }
                    ],
                    "volumes": [
                        {
                            "name": neo4j_volume_name,
                            "persistentVolumeClaim": {
                                "claimName": neo4j_claim_name,
                            },
                        }
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        settings.neo4j_name,
        metadata=namespaced_metadata(namespace_name, settings.neo4j_name),
        spec={
            "selector": neo4j_labels,
            "ports": [
                {
                    "name": "http",
                    "port": settings.neo4j_http_port,
                    "targetPort": settings.neo4j_http_port,
                },
                {
                    "name": "bolt",
                    "port": settings.neo4j_bolt_port,
                    "targetPort": settings.neo4j_bolt_port,
                },
            ],
        },
    )
