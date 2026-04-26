from typing import Sequence

import pulumi
import pulumi_kubernetes as k8s

from common import labels, namespaced_metadata
from settings import Settings


def create_frontend(
    settings: Settings,
    namespace_name: pulumi.Input[str],
    app_service_name: pulumi.Input[str],
    dependencies: Sequence[pulumi.Resource] | None = None,
) -> k8s.core.v1.Service:
    frontend_labels = labels(settings.frontend_name)

    k8s.apps.v1.Deployment(
        settings.frontend_name,
        metadata=namespaced_metadata(namespace_name, settings.frontend_name),
        spec={
            "selector": {
                "matchLabels": frontend_labels,
            },
            "replicas": settings.frontend_replicas,
            "template": {
                "metadata": {
                    "labels": frontend_labels,
                },
                "spec": {
                    "containers": [
                        {
                            "name": settings.frontend_name,
                            "image": settings.frontend_image,
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "containerPort": settings.frontend_port,
                                }
                            ],
                            "env": [
                                {
                                    "name": "NEXT_PUBLIC_API_URL",
                                    "value": pulumi.Output.concat(
                                        "http://", app_service_name, ":", str(settings.app_port)
                                    ),
                                },
                            ],
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": settings.frontend_port,
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 10,
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/",
                                    "port": settings.frontend_port,
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
        settings.frontend_name,
        metadata=namespaced_metadata(namespace_name, settings.frontend_name),
        spec={
            "selector": frontend_labels,
            "ports": [
                {
                    "port": settings.frontend_port,
                    "targetPort": settings.frontend_port,
                }
            ],
        },
    )
