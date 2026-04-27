DEFAULT_APP_NAME = "arch-review-api"
DEFAULT_APP_PORT = 8000
DEFAULT_FRONTEND_NAME = "arch-review-frontend"
DEFAULT_FRONTEND_PORT = 3000
DEFAULT_PGVECTOR_NAME = "pgvector"
DEFAULT_PGVECTOR_PORT = 5432
DEFAULT_NEO4J_NAME = "neo4j"
DEFAULT_NEO4J_HTTP_PORT = 7474
DEFAULT_NEO4J_BOLT_PORT = 7687
DEFAULT_TRAEFIK_NAME = "traefik"
DEFAULT_TRAEFIK_NAMESPACE = "traefik"
DEFAULT_TRAEFIK_HTTP_NODE_PORT = 30080
DEFAULT_TRAEFIK_HTTPS_NODE_PORT = 30443
DEFAULT_TRAEFIK_INGRESS_CLASS = "traefik"

DEFAULT_TEMPO_NAME = "tempo"
DEFAULT_TEMPO_HTTP_PORT = 3200
DEFAULT_TEMPO_OTLP_GRPC_PORT = 4317
DEFAULT_TEMPO_OTLP_HTTP_PORT = 4318

DEFAULT_LOKI_NAME = "loki"
DEFAULT_LOKI_PORT = 3100

DEFAULT_PROMETHEUS_NAME = "prometheus"
DEFAULT_PROMETHEUS_PORT = 9090

DEFAULT_GRAFANA_NAME = "grafana"
DEFAULT_GRAFANA_PORT = 3000
DEFAULT_GRAFANA_NODE_PORT = 30300


def secret_key_ref(name: str, key: str) -> dict[str, object]:
    return {
        "secretKeyRef": {
            "name": name,
            "key": key,
        }
    }


def labels(app_name: str) -> dict[str, str]:
    return {"app": app_name}


def namespaced_metadata(namespace_name, name: str) -> dict[str, object]:
    return {
        "namespace": namespace_name,
        "name": name,
    }


def related_name(base_name: str, suffix: str) -> str:
    return f"{base_name}-{suffix}"
