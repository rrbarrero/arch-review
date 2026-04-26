APP_NAME = "arch-review-api"
APP_PORT = 8000
TRAEFIK_NAME = "traefik"
TRAEFIK_NAMESPACE = "traefik"
TRAEFIK_HTTP_NODE_PORT = 30080
TRAEFIK_HTTPS_NODE_PORT = 30443
TRAEFIK_INGRESS_CLASS = "traefik"


def labels(app_name: str) -> dict[str, str]:
    return {"app": app_name}


def namespaced_metadata(namespace_name, name: str) -> dict[str, object]:
    return {
        "namespace": namespace_name,
        "name": name,
    }
