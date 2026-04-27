import hashlib

import pulumi
import pulumi_kubernetes as k8s

from common import labels, namespaced_metadata, related_name
from settings import Settings

TEMPO_CONFIG = """\
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: "0.0.0.0:4317"
        http:
          endpoint: "0.0.0.0:4318"

storage:
  trace:
    backend: local
    local:
      path: /var/tempo/blocks
    pool:
      max_workers: 100
"""

PROMETHEUS_CONFIG = """\
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'arch-review'
    metrics_path: '/metrics/'
    static_configs:
      - targets: ['arch-review-api:8000']
"""

GRAFANA_DATASOURCES = """\
apiVersion: 1

datasources:
  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    uid: tempo

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    uid: loki
    isDefault: true
    jsonData:
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\\\w+)"
          name: trace_id
          url: "$${__value.raw}"

  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    uid: prometheus
"""

DASHBOARD_PROVIDER = """\
apiVersion: 1
providers:
  - name: "Arch Review"
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
"""

DASHBOARD_JSON = """\
{
  "title": "Arch Review",
  "uid": "arch-review",
  "version": 1,
  "timezone": "browser",
  "panels": [
    {
      "title": "HTTP Requests Rate",
      "type": "timeseries",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 0, "y": 0, "w": 8, "h": 8},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "rate(http_requests_total{path!~'/metrics.*'}[1m])",
          "legendFormat": "{{method}} {{path}}"
        }
      ]
    },
    {
      "title": "HTTP Request Duration (p95)",
      "type": "timeseries",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 8, "y": 0, "w": 8, "h": 8},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{path!~'/metrics.*'}[1m]))",
          "legendFormat": "p95 {{method}} {{path}}"
        }
      ]
    },
    {
      "title": "HTTP Request Duration (p50)",
      "type": "timeseries",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 16, "y": 0, "w": 8, "h": 8},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "histogram_quantile(0.5, rate(http_request_duration_seconds_bucket{path!~'/metrics.*'}[1m]))",
          "legendFormat": "p50 {{method}} {{path}}"
        }
      ]
    },
    {
      "title": "Documents Ingested",
      "type": "stat",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 0, "y": 8, "w": 4, "h": 6},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "sum(documents_ingested_total)"
        }
      ]
    },
    {
      "title": "Questions Answered",
      "type": "stat",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 4, "y": 8, "w": 4, "h": 6},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "sum(questions_answered_total)"
        }
      ]
    },
    {
      "title": "Ingest Errors",
      "type": "stat",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 8, "y": 8, "w": 4, "h": 6},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "sum(documents_ingest_errors_total)"
        }
      ]
    },
    {
      "title": "Documents Ingested by Type",
      "type": "piechart",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 12, "y": 8, "w": 6, "h": 6},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "sum by (content_type) (documents_ingested_total)"
        }
      ]
    },
    {
      "title": "Ingest Errors by Reason",
      "type": "piechart",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 18, "y": 8, "w": 6, "h": 6},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "sum by (reason) (documents_ingest_errors_total)"
        }
      ]
    },
    {
      "title": "Chunks Retrieved per Question",
      "type": "timeseries",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 0, "y": 14, "w": 8, "h": 8},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "rate(context_chunks_retrieved_sum[1m]) / rate(context_chunks_retrieved_count[1m])",
          "legendFormat": "avg chunks"
        }
      ]
    },
    {
      "title": "Chunks Created",
      "type": "timeseries",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 8, "y": 14, "w": 8, "h": 8},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "rate(chunks_created_total[1m])",
          "legendFormat": "{{content_type}}"
        }
      ]
    },
    {
      "title": "Chunks Embedded",
      "type": "timeseries",
      "datasource": {"type": "prometheus", "uid": "prometheus"},
      "gridPos": {"x": 16, "y": 14, "w": 8, "h": 8},
      "targets": [
        {
          "datasource": {"type": "prometheus", "uid": "prometheus"},
          "expr": "rate(chunks_embedded_total[1m])"
        }
      ]
    }
  ]
}
"""


def create_tempo(settings: Settings, namespace_name: pulumi.Input[str]) -> k8s.core.v1.Service:
    name = settings.tempo_name
    tempo_labels = labels(name)
    claim_name = related_name(name, "pvc")
    volume_name = related_name(name, "data")

    k8s.core.v1.ConfigMap(
        f"{name}-config",
        metadata=namespaced_metadata(namespace_name, f"{name}-config"),
        data={
            "tempo.yaml": TEMPO_CONFIG,
        },
    )

    k8s.core.v1.PersistentVolumeClaim(
        claim_name,
        metadata=namespaced_metadata(namespace_name, claim_name),
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "256Mi"}},
        },
    )

    k8s.apps.v1.Deployment(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": {"matchLabels": tempo_labels},
            "replicas": 1,
            "template": {
                "metadata": {"labels": tempo_labels},
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": settings.tempo_image,
                            "args": ["-config.file=/etc/tempo.yaml"],
                            "ports": [
                                {"containerPort": settings.tempo_http_port, "name": "http"},
                                {"containerPort": settings.tempo_otlp_grpc_port, "name": "otlp-grpc"},
                                {"containerPort": settings.tempo_otlp_http_port, "name": "otlp-http"},
                            ],
                            "volumeMounts": [
                                {"name": "config", "mountPath": "/etc/tempo.yaml", "subPath": "tempo.yaml"},
                                {"name": volume_name, "mountPath": "/var/tempo"},
                            ],
                        }
                    ],
                    "volumes": [
                        {"name": "config", "configMap": {"name": f"{name}-config"}},
                        {"name": volume_name, "persistentVolumeClaim": {"claimName": claim_name}},
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": tempo_labels,
            "ports": [
                {"name": "http", "port": settings.tempo_http_port, "targetPort": settings.tempo_http_port},
                {"name": "otlp-grpc", "port": settings.tempo_otlp_grpc_port, "targetPort": settings.tempo_otlp_grpc_port},
                {"name": "otlp-http", "port": settings.tempo_otlp_http_port, "targetPort": settings.tempo_otlp_http_port},
            ],
        },
    )


def create_loki(settings: Settings, namespace_name: pulumi.Input[str]) -> k8s.core.v1.Service:
    name = settings.loki_name
    loki_labels = labels(name)
    claim_name = related_name(name, "pvc")

    k8s.core.v1.PersistentVolumeClaim(
        claim_name,
        metadata=namespaced_metadata(namespace_name, claim_name),
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "256Mi"}},
        },
    )

    k8s.apps.v1.Deployment(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": {"matchLabels": loki_labels},
            "replicas": 1,
            "template": {
                "metadata": {"labels": loki_labels},
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": settings.loki_image,
                            "ports": [
                                {"containerPort": settings.loki_port, "name": "http"},
                            ],
                            "volumeMounts": [
                                {"name": "data", "mountPath": "/loki"},
                            ],
                        }
                    ],
                    "volumes": [
                        {"name": "data", "persistentVolumeClaim": {"claimName": claim_name}},
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": loki_labels,
            "ports": [
                {"name": "http", "port": settings.loki_port, "targetPort": settings.loki_port},
            ],
        },
    )


def create_prometheus(settings: Settings, namespace_name: pulumi.Input[str]) -> k8s.core.v1.Service:
    name = settings.prometheus_name
    prometheus_labels = labels(name)
    claim_name = related_name(name, "pvc")

    k8s.core.v1.ConfigMap(
        f"{name}-config",
        metadata=namespaced_metadata(namespace_name, f"{name}-config"),
        data={
            "prometheus.yml": PROMETHEUS_CONFIG,
        },
    )

    k8s.core.v1.PersistentVolumeClaim(
        claim_name,
        metadata=namespaced_metadata(namespace_name, claim_name),
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "256Mi"}},
        },
    )

    k8s.apps.v1.Deployment(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": {"matchLabels": prometheus_labels},
            "replicas": 1,
            "template": {
                "metadata": {"labels": prometheus_labels},
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": settings.prometheus_image,
                            "args": ["--config.file=/etc/prometheus/prometheus.yml"],
                            "ports": [
                                {"containerPort": settings.prometheus_port, "name": "http"},
                            ],
                            "volumeMounts": [
                                {
                                    "name": "config",
                                    "mountPath": "/etc/prometheus/prometheus.yml",
                                    "subPath": "prometheus.yml",
                                },
                                {"name": "data", "mountPath": "/prometheus"},
                            ],
                        }
                    ],
                    "volumes": [
                        {"name": "config", "configMap": {"name": f"{name}-config"}},
                        {"name": "data", "persistentVolumeClaim": {"claimName": claim_name}},
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": prometheus_labels,
            "ports": [
                {"name": "http", "port": settings.prometheus_port, "targetPort": settings.prometheus_port},
            ],
        },
    )


def create_grafana(
    settings: Settings,
    namespace_name: pulumi.Input[str],
    dependencies: pulumi.Resource | None = None,
) -> k8s.core.v1.Service:
    name = settings.grafana_name
    grafana_labels = labels(name)
    claim_name = related_name(name, "pvc")

    k8s.core.v1.ConfigMap(
        f"{name}-datasources",
        metadata=namespaced_metadata(namespace_name, f"{name}-datasources"),
        data={
            "datasources.yml": GRAFANA_DATASOURCES,
        },
    )

    k8s.core.v1.ConfigMap(
        f"{name}-dashboard-provider",
        metadata=namespaced_metadata(namespace_name, f"{name}-dashboard-provider"),
        data={
            "dashboard-provider.yml": DASHBOARD_PROVIDER,
        },
    )

    k8s.core.v1.ConfigMap(
        f"{name}-dashboard",
        metadata=namespaced_metadata(namespace_name, f"{name}-dashboard"),
        data={
            "arch-review.json": DASHBOARD_JSON,
        },
    )

    k8s.core.v1.PersistentVolumeClaim(
        claim_name,
        metadata=namespaced_metadata(namespace_name, claim_name),
        spec={
            "accessModes": ["ReadWriteOnce"],
            "resources": {"requests": {"storage": "256Mi"}},
        },
    )

    config_hash = hashlib.sha256(
        (GRAFANA_DATASOURCES + DASHBOARD_PROVIDER + DASHBOARD_JSON).encode()
    ).hexdigest()[:12]

    k8s.apps.v1.Deployment(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": {"matchLabels": grafana_labels},
            "replicas": 1,
            "template": {
                "metadata": {
                    "labels": grafana_labels,
                    "annotations": {
                        "pulumi.com/configHash": config_hash,
                    },
                },
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": settings.grafana_image,
                            "ports": [
                                {"containerPort": settings.grafana_port, "name": "http"},
                            ],
                            "env": [
                                {"name": "GF_AUTH_ANONYMOUS_ENABLED", "value": "true"},
                            ],
                            "volumeMounts": [
                                {
                                    "name": "datasources",
                                    "mountPath": "/etc/grafana/provisioning/datasources/datasources.yml",
                                    "subPath": "datasources.yml",
                                },
                                {
                                    "name": "dashboard-provider",
                                    "mountPath": "/etc/grafana/provisioning/dashboards/dashboard-provider.yml",
                                    "subPath": "dashboard-provider.yml",
                                },
                                {
                                    "name": "dashboard",
                                    "mountPath": "/etc/grafana/provisioning/dashboards/arch-review.json",
                                    "subPath": "arch-review.json",
                                },
                                {"name": "data", "mountPath": "/var/lib/grafana"},
                            ],
                        }
                    ],
                    "volumes": [
                        {
                            "name": "datasources",
                            "configMap": {"name": f"{name}-datasources"},
                        },
                        {
                            "name": "dashboard-provider",
                            "configMap": {"name": f"{name}-dashboard-provider"},
                        },
                        {
                            "name": "dashboard",
                            "configMap": {"name": f"{name}-dashboard"},
                        },
                        {"name": "data", "persistentVolumeClaim": {"claimName": claim_name}},
                    ],
                },
            },
        },
    )

    return k8s.core.v1.Service(
        name,
        metadata=namespaced_metadata(namespace_name, name),
        spec={
            "selector": grafana_labels,
            "ports": [
                {"name": "http", "port": settings.grafana_port, "targetPort": settings.grafana_port},
            ],
        },
    )


def create_grafana_ingress(
    settings: Settings,
    namespace_name: pulumi.Input[str],
    grafana_service_name: pulumi.Input[str],
    dependencies: pulumi.Resource | None = None,
) -> None:
    k8s.networking.v1.Ingress(
        settings.grafana_name,
        metadata={
            **namespaced_metadata(namespace_name, settings.grafana_name),
            "annotations": {
                "pulumi.com/skipAwait": "true",
            },
        },
        spec={
            "ingressClassName": settings.traefik_ingress_class,
            "rules": [
                {
                    "host": settings.grafana_host,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": grafana_service_name,
                                        "port": {"number": settings.grafana_port},
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
