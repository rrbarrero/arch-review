import pulumi

from app_resources import create_app, create_ingress, create_namespace
from data_resources import create_neo4j, create_pgvector
from frontend_resources import create_frontend
from observability_resources import (
    create_grafana,
    create_grafana_ingress,
    create_loki,
    create_prometheus,
    create_tempo,
)
from settings import Settings, load_settings
from shared_resources import create_traefik


def main(settings: Settings | None = None) -> None:
    resolved_settings = settings or load_settings()

    namespace_name = create_namespace(resolved_settings)
    pgvector_service = create_pgvector(resolved_settings, namespace_name)
    neo4j_service = create_neo4j(resolved_settings, namespace_name)

    tempo_service = create_tempo(resolved_settings, namespace_name)
    loki_service = create_loki(resolved_settings, namespace_name)
    prometheus_service = create_prometheus(resolved_settings, namespace_name)
    grafana_service = create_grafana(resolved_settings, namespace_name)

    app_service = create_app(
        resolved_settings,
        namespace_name,
        dependencies=[pgvector_service, neo4j_service, tempo_service],
    )
    frontend_service = create_frontend(
        resolved_settings,
        namespace_name,
        app_service.metadata["name"],
        dependencies=[app_service],
    )

    ingress_dependencies = [app_service]
    if resolved_settings.install_traefik:
        ingress_dependencies.append(create_traefik(resolved_settings))

    create_ingress(
        resolved_settings,
        namespace_name,
        ingress_dependencies,
    )

    create_grafana_ingress(
        resolved_settings,
        namespace_name,
        grafana_service.metadata["name"],
        dependencies=ingress_dependencies,
    )

    pulumi.export("namespace", namespace_name)
    pulumi.export("image", resolved_settings.image)
    pulumi.export("frontend_image", resolved_settings.frontend_image)
    pulumi.export("pgvector_service", pgvector_service.metadata["name"])
    pulumi.export("neo4j_service", neo4j_service.metadata["name"])
    pulumi.export("frontend_service", frontend_service.metadata["name"])
    pulumi.export("tempo_service", tempo_service.metadata["name"])
    pulumi.export("loki_service", loki_service.metadata["name"])
    pulumi.export("prometheus_service", prometheus_service.metadata["name"])
    pulumi.export("grafana_service", grafana_service.metadata["name"])
    pulumi.export("ingress_host", resolved_settings.ingress_host)
    pulumi.export("grafana_host", resolved_settings.grafana_host)
    pulumi.export(
        "ingress_url",
        pulumi.Output.concat("http://", resolved_settings.ingress_host, ":30080"),
    )
    pulumi.export(
        "grafana_url",
        pulumi.Output.concat("http://", resolved_settings.grafana_host, ":30080"),
    )
