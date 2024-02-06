from kubernetes import client, config
from kubernetes.client.rest import ApiException
import click
import time

@click.command()
@click.option("--base_pod_name", default=None, show_default=True, type=str)
@click.option("--namespace", type=str)
def main(base_pod_name, namespace):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    pod_names = [pod.metadata.name for pod in pods.items]
    # Pod name should have rand string
    for pod_name in pod_names:
        if base_pod_name in pod_name:
            pod = pod_name
            break
    else:
        raise ValueError(f"Pod:{base_pod_name} not found in available pods {pod_names}")
    
    status = ""
    start_idx = 0
    while status not in ("Failed", "Succeeded"):
        status = v1.read_namespaced_pod(name=pod, namespace=namespace).status.phase
        try:
            pod_log = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
            if pod_log[start_idx:]:
                click.echo(pod_log[start_idx:])
                start_idx = len(pod_log)
        except ApiException:
            pass
        time.sleep(0.5)
    
    time.sleep(4)

    pod_log = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
    click.echo(pod_log[start_idx:])

    v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
    
if __name__ == "__main__":
    main()    

    
    
