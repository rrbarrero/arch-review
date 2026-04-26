import pulumi_kubernetes as k8s

from settings import Settings


def create_traefik(settings: Settings) -> k8s.helm.v3.Release:
    return k8s.helm.v3.Release(
        settings.traefik_name,
        name=settings.traefik_name,
        chart=settings.traefik_name,
        repository_opts={
            "repo": "https://traefik.github.io/charts",
        },
        namespace=settings.traefik_namespace,
        create_namespace=True,
        values={
            "service": {
                "type": "NodePort",
            },
            "ingressClass": {
                "enabled": True,
                "isDefaultClass": False,
                "name": settings.traefik_ingress_class,
            },
            "ports": {
                "web": {
                    "nodePort": settings.traefik_http_node_port,
                },
                "websecure": {
                    "nodePort": settings.traefik_https_node_port,
                },
            },
            "providers": {
                "kubernetesIngress": {
                    "ingressClass": settings.traefik_ingress_class,
                },
                "kubernetesCRD": {
                    "ingressClass": settings.traefik_ingress_class,
                },
            },
        },
    )
