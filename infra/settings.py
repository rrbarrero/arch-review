from dataclasses import dataclass

import pulumi


@dataclass(frozen=True)
class Settings:
    namespace: str
    image: str
    replicas: int
    ingress_host: str
    install_traefik: bool


def load_settings() -> Settings:
    config = pulumi.Config()
    namespace = config.require("namespace")
    image = config.require("image")
    replicas = config.get_int("replicas") or 1
    ingress_host = config.require("ingress_host")
    install_traefik = config.get_bool("install_traefik")

    if not namespace:
        raise pulumi.RunError("Config 'namespace' must not be empty")
    if not image:
        raise pulumi.RunError("Config 'image' must not be empty")
    if replicas < 1:
        raise pulumi.RunError("Config 'replicas' must be greater than zero")
    if not ingress_host or "://" in ingress_host or "/" in ingress_host:
        raise pulumi.RunError("Config 'ingress_host' must be a hostname")

    return Settings(
        namespace=namespace,
        image=image,
        replicas=replicas,
        ingress_host=ingress_host,
        install_traefik=install_traefik if install_traefik is not None else True,
    )
