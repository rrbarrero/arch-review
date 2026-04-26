import pulumi

from app_resources import create_app, create_ingress, create_namespace
from settings import Settings, load_settings
from shared_resources import create_traefik


def main(settings: Settings | None = None) -> None:
    resolved_settings = settings or load_settings()

    namespace_name = create_namespace(resolved_settings)
    app_service = create_app(resolved_settings, namespace_name)

    ingress_dependencies = [app_service]
    if resolved_settings.install_traefik:
        ingress_dependencies.append(create_traefik())

    create_ingress(
        namespace_name,
        resolved_settings.ingress_host,
        ingress_dependencies,
    )

    pulumi.export("namespace", namespace_name)
    pulumi.export("image", resolved_settings.image)
    pulumi.export("ingress_host", resolved_settings.ingress_host)
    pulumi.export(
        "ingress_url",
        pulumi.Output.concat("http://", resolved_settings.ingress_host, ":30080"),
    )
