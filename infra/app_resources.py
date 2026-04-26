from typing import Sequence

import pulumi
import pulumi_kubernetes as k8s

from common import APP_NAME, APP_PORT, TRAEFIK_INGRESS_CLASS, labels, namespaced_metadata
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
) -> k8s.core.v1.Service:
    app_labels = labels(APP_NAME)

    k8s.apps.v1.Deployment(
        APP_NAME,
        metadata=namespaced_metadata(namespace_name, APP_NAME),
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
                            "name": APP_NAME,
                            "image": settings.image,
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "containerPort": APP_PORT,
                                }
                            ],
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": APP_PORT,
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 10,
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": APP_PORT,
                                },
                                "initialDelaySeconds": 15,
                                "periodSeconds": 20,
                            },
                        }
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        APP_NAME,
        metadata=namespaced_metadata(namespace_name, APP_NAME),
        spec={
            "selector": app_labels,
            "ports": [
                {
                    "port": APP_PORT,
                    "targetPort": APP_PORT,
                }
            ],
        },
    )


def create_ingress(
    namespace_name: pulumi.Input[str],
    ingress_host: str,
    dependencies: Sequence[pulumi.Resource],
) -> None:
    k8s.networking.v1.Ingress(
        APP_NAME,
        metadata={
            **namespaced_metadata(namespace_name, APP_NAME),
            "annotations": {
                "pulumi.com/skipAwait": "true",
            },
        },
        spec={
            "ingressClassName": TRAEFIK_INGRESS_CLASS,
            "rules": [
                {
                    "host": ingress_host,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": APP_NAME,
                                        "port": {
                                            "number": APP_PORT,
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
