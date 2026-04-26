import pulumi

from app_resources import create_app, create_ingress, create_namespace
from data_resources import create_neo4j, create_pgvector
from settings import Settings, load_settings
from shared_resources import create_traefik


def main(settings: Settings | None = None) -> None:
    resolved_settings = settings or load_settings()

    namespace_name = create_namespace(resolved_settings)
    pgvector_service = create_pgvector(resolved_settings, namespace_name)
    neo4j_service = create_neo4j(resolved_settings, namespace_name)
    app_service = create_app(
        resolved_settings,
        namespace_name,
        dependencies=[pgvector_service, neo4j_service],
    )

    ingress_dependencies = [app_service]
    if resolved_settings.install_traefik:
        ingress_dependencies.append(create_traefik(resolved_settings))

    create_ingress(
        resolved_settings,
        namespace_name,
        ingress_dependencies,
    )

    pulumi.export("namespace", namespace_name)
    pulumi.export("image", resolved_settings.image)
    pulumi.export("pgvector_service", pgvector_service.metadata["name"])
    pulumi.export("neo4j_service", neo4j_service.metadata["name"])
    pulumi.export("ingress_host", resolved_settings.ingress_host)
    pulumi.export(
        "ingress_url",
        pulumi.Output.concat("http://", resolved_settings.ingress_host, ":30080"),
    )
