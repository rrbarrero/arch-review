from dataclasses import dataclass

import pulumi

from common import (
    DEFAULT_APP_NAME,
    DEFAULT_APP_PORT,
    DEFAULT_FRONTEND_NAME,
    DEFAULT_FRONTEND_PORT,
    DEFAULT_GRAFANA_NAME,
    DEFAULT_GRAFANA_PORT,
    DEFAULT_LOKI_NAME,
    DEFAULT_LOKI_PORT,
    DEFAULT_NEO4J_BOLT_PORT,
    DEFAULT_NEO4J_HTTP_PORT,
    DEFAULT_NEO4J_NAME,
    DEFAULT_PGVECTOR_NAME,
    DEFAULT_PGVECTOR_PORT,
    DEFAULT_PROMETHEUS_NAME,
    DEFAULT_PROMETHEUS_PORT,
    DEFAULT_TEMPO_NAME,
    DEFAULT_TEMPO_HTTP_PORT,
    DEFAULT_TEMPO_OTLP_GRPC_PORT,
    DEFAULT_TEMPO_OTLP_HTTP_PORT,
    DEFAULT_TRAEFIK_HTTPS_NODE_PORT,
    DEFAULT_TRAEFIK_HTTP_NODE_PORT,
    DEFAULT_TRAEFIK_INGRESS_CLASS,
    DEFAULT_TRAEFIK_NAME,
    DEFAULT_TRAEFIK_NAMESPACE,
)


@dataclass(frozen=True)
class Settings:
    namespace: str
    app_name: str
    app_port: int
    image: str
    replicas: int
    ingress_host: str
    install_traefik: bool
    traefik_name: str
    traefik_namespace: str
    traefik_http_node_port: int
    traefik_https_node_port: int
    traefik_ingress_class: str
    frontend_name: str
    frontend_port: int
    frontend_image: str
    frontend_replicas: int
    pgvector_name: str
    pgvector_port: int
    pgvector_image: str
    pgvector_db: str
    pgvector_user: str
    pgvector_password: pulumi.Output[str]
    pgvector_storage_size: str
    neo4j_name: str
    neo4j_http_port: int
    neo4j_bolt_port: int
    neo4j_image: str
    neo4j_user: str
    neo4j_password: pulumi.Output[str]
    neo4j_storage_size: str
    ollama_base_url: str
    llm_model: str
    llm_temperature: float
    embedding_model: str
    cors_origins_raw: str

    tempo_name: str
    tempo_image: str
    tempo_http_port: int
    tempo_otlp_grpc_port: int
    tempo_otlp_http_port: int
    loki_name: str
    loki_image: str
    loki_port: int
    prometheus_name: str
    prometheus_image: str
    prometheus_port: int
    grafana_name: str
    grafana_image: str
    grafana_port: int
    grafana_host: str


def load_settings() -> Settings:
    config = pulumi.Config()
    namespace = config.require("namespace")
    app_name = config.get("app_name") or DEFAULT_APP_NAME
    app_port = config.get_int("app_port") or DEFAULT_APP_PORT
    image = config.require("image")
    replicas = config.get_int("replicas") or 1
    ingress_host = config.require("ingress_host")
    install_traefik = config.get_bool("install_traefik")
    traefik_name = config.get("traefik_name") or DEFAULT_TRAEFIK_NAME
    traefik_namespace = config.get("traefik_namespace") or DEFAULT_TRAEFIK_NAMESPACE
    traefik_http_node_port = (
        config.get_int("traefik_http_node_port") or DEFAULT_TRAEFIK_HTTP_NODE_PORT
    )
    traefik_https_node_port = (
        config.get_int("traefik_https_node_port") or DEFAULT_TRAEFIK_HTTPS_NODE_PORT
    )
    traefik_ingress_class = (
        config.get("traefik_ingress_class") or DEFAULT_TRAEFIK_INGRESS_CLASS
    )
    frontend_name = config.get("frontend_name") or DEFAULT_FRONTEND_NAME
    frontend_port = config.get_int("frontend_port") or DEFAULT_FRONTEND_PORT
    frontend_image = config.require("frontend_image")
    frontend_replicas = config.get_int("frontend_replicas") or 1
    pgvector_name = config.get("pgvector_name") or DEFAULT_PGVECTOR_NAME
    pgvector_port = config.get_int("pgvector_port") or DEFAULT_PGVECTOR_PORT
    pgvector_image = config.get("pgvector_image") or "pgvector/pgvector:pg16"
    pgvector_db = config.get("pgvector_db") or "arch_review"
    pgvector_user = config.get("pgvector_user") or "arch_review"
    pgvector_password = config.get_secret("pgvector_password") or pulumi.Output.secret(
        "arch-review-dev"
    )
    pgvector_storage_size = config.get("pgvector_storage_size") or "1Gi"
    neo4j_name = config.get("neo4j_name") or DEFAULT_NEO4J_NAME
    neo4j_http_port = config.get_int("neo4j_http_port") or DEFAULT_NEO4J_HTTP_PORT
    neo4j_bolt_port = config.get_int("neo4j_bolt_port") or DEFAULT_NEO4J_BOLT_PORT
    neo4j_image = config.get("neo4j_image") or "neo4j:5-community"
    neo4j_user = config.get("neo4j_user") or "neo4j"
    neo4j_password = config.get_secret("neo4j_password") or pulumi.Output.secret(
        "arch-review-dev"
    )
    neo4j_storage_size = config.get("neo4j_storage_size") or "1Gi"
    ollama_base_url = config.get("ollama_base_url") or "http://ollama:11434"
    llm_model = config.get("llm_model") or "qwen3-8b-12k:latest"
    llm_temperature = config.get_float("llm_temperature") or 0.0
    embedding_model = config.get("embedding_model") or "bge-m3:latest"
    cors_origins_raw = config.get("cors_origins_raw") or (
        f"http://{ingress_host}:{traefik_http_node_port}"
    )

    tempo_name = config.get("tempo_name") or DEFAULT_TEMPO_NAME
    tempo_image = config.get("tempo_image") or "grafana/tempo:latest"
    tempo_http_port = config.get_int("tempo_http_port") or DEFAULT_TEMPO_HTTP_PORT
    tempo_otlp_grpc_port = config.get_int("tempo_otlp_grpc_port") or DEFAULT_TEMPO_OTLP_GRPC_PORT
    tempo_otlp_http_port = config.get_int("tempo_otlp_http_port") or DEFAULT_TEMPO_OTLP_HTTP_PORT
    loki_name = config.get("loki_name") or DEFAULT_LOKI_NAME
    loki_image = config.get("loki_image") or "grafana/loki:latest"
    loki_port = config.get_int("loki_port") or DEFAULT_LOKI_PORT
    prometheus_name = config.get("prometheus_name") or DEFAULT_PROMETHEUS_NAME
    prometheus_image = config.get("prometheus_image") or "prom/prometheus:latest"
    prometheus_port = config.get_int("prometheus_port") or DEFAULT_PROMETHEUS_PORT
    grafana_name = config.get("grafana_name") or DEFAULT_GRAFANA_NAME
    grafana_image = config.get("grafana_image") or "grafana/grafana:latest"
    grafana_port = config.get_int("grafana_port") or DEFAULT_GRAFANA_PORT
    grafana_host = config.get("grafana_host") or f"grafana.{ingress_host}"

    if not namespace:
        raise pulumi.RunError("Config 'namespace' must not be empty")
    if not image:
        raise pulumi.RunError("Config 'image' must not be empty")
    if not frontend_image:
        raise pulumi.RunError("Config 'frontend_image' must not be empty")
    for key, value in {
        "app_port": app_port,
        "replicas": replicas,
        "frontend_port": frontend_port,
        "frontend_replicas": frontend_replicas,
        "traefik_http_node_port": traefik_http_node_port,
        "traefik_https_node_port": traefik_https_node_port,
        "pgvector_port": pgvector_port,
        "neo4j_http_port": neo4j_http_port,
        "neo4j_bolt_port": neo4j_bolt_port,
    }.items():
        if value < 1:
            raise pulumi.RunError(f"Config '{key}' must be greater than zero")
    if not ingress_host or "://" in ingress_host or "/" in ingress_host:
        raise pulumi.RunError("Config 'ingress_host' must be a hostname")
    for key, value in {
        "app_name": app_name,
        "frontend_name": frontend_name,
        "traefik_name": traefik_name,
        "traefik_namespace": traefik_namespace,
        "traefik_ingress_class": traefik_ingress_class,
        "pgvector_name": pgvector_name,
        "pgvector_image": pgvector_image,
        "pgvector_db": pgvector_db,
        "pgvector_user": pgvector_user,
        "pgvector_storage_size": pgvector_storage_size,
        "neo4j_name": neo4j_name,
        "neo4j_image": neo4j_image,
        "neo4j_user": neo4j_user,
        "neo4j_storage_size": neo4j_storage_size,
    }.items():
        if not value:
            raise pulumi.RunError(f"Config '{key}' must not be empty")

    return Settings(
        namespace=namespace,
        app_name=app_name,
        app_port=app_port,
        image=image,
        replicas=replicas,
        ingress_host=ingress_host,
        install_traefik=install_traefik if install_traefik is not None else True,
        traefik_name=traefik_name,
        traefik_namespace=traefik_namespace,
        traefik_http_node_port=traefik_http_node_port,
        traefik_https_node_port=traefik_https_node_port,
        traefik_ingress_class=traefik_ingress_class,
        frontend_name=frontend_name,
        frontend_port=frontend_port,
        frontend_image=frontend_image,
        frontend_replicas=frontend_replicas,
        pgvector_name=pgvector_name,
        pgvector_port=pgvector_port,
        pgvector_image=pgvector_image,
        pgvector_db=pgvector_db,
        pgvector_user=pgvector_user,
        pgvector_password=pgvector_password,
        pgvector_storage_size=pgvector_storage_size,
        neo4j_name=neo4j_name,
        neo4j_http_port=neo4j_http_port,
        neo4j_bolt_port=neo4j_bolt_port,
        neo4j_image=neo4j_image,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        neo4j_storage_size=neo4j_storage_size,
        ollama_base_url=ollama_base_url,
        llm_model=llm_model,
        llm_temperature=llm_temperature,
        embedding_model=embedding_model,
        cors_origins_raw=cors_origins_raw,

        tempo_name=tempo_name,
        tempo_image=tempo_image,
        tempo_http_port=tempo_http_port,
        tempo_otlp_grpc_port=tempo_otlp_grpc_port,
        tempo_otlp_http_port=tempo_otlp_http_port,
        loki_name=loki_name,
        loki_image=loki_image,
        loki_port=loki_port,
        prometheus_name=prometheus_name,
        prometheus_image=prometheus_image,
        prometheus_port=prometheus_port,
        grafana_name=grafana_name,
        grafana_image=grafana_image,
        grafana_port=grafana_port,
        grafana_host=grafana_host,
    )
