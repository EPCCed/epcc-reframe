from kubernetes import client, config
from kubernetes.client.rest import ApiException
import click
import time
import yaml
import json
import re

@click.command()
@click.option("--base_pod_name", default=None, show_default=True, type=str)
@click.option("--namespace", type=str)
@click.option("--pod_yaml", type=str)
def main(base_pod_name, namespace, pod_yaml):
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        
        with open(pod_yaml, "r") as stream:
            pod_def = yaml.safe_load(stream)
        
        while True:
            try:
                v1.create_namespaced_pod(body=pod_def, namespace=namespace)
                click.echo(f"Pod {base_pod_name} Create")
            except ApiException as e:
                body = json.loads(e.body)["message"]
                if "exceeded quota:" in body:
                    if "gpu" not in body:
                        raise ValueError(f"Quota Exceeded See: {e.body}")
                    num_gpus = pod_def["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"]
                    limit = re.search(r'limited: requests.nvidia.com/gpu=(\d+)', body)
                    if num_gpus > int(limit.group(1)):
                        raise ValueError(f"Requested {num_gpus} GPU, namespace limited to {limit} GPUs")
                    print("Maximum Quota Resources In Use Trying Again In 60s")
                    time.sleep(60)
                    continue
                else:
                    raise e
            break
                
        
        pods = v1.list_namespaced_pod(namespace)
        pod_names = [pod.metadata.name for pod in pods.items]
        # Pod name should have rand string
        count = 1
        while True:
            for pod_name in pod_names:
                if base_pod_name in pod_name:
                    pod = pod_name
                    print(f"Reframe Found Pod:{pod}")
                    break
            else:
                # Allow 2 minutes 
                
                if count == 12:
                    raise ValueError(f"Pod:{base_pod_name} not found in available pods {pod_names}")
                click.echo(f"Pod:{base_pod_name} not found in available pods {pod_names}")
                time.sleep(10)
                count += 1
                continue
            break
        
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
        print(f"Pod {base_pod_name} Deleted")
    except KeyboardInterrupt:
        while True:
            for pod_name in pod_names:
                if base_pod_name in pod_name:
                    pod = pod_name
                    print(f"Reframe Found Pod:{pod}")
                    break
            else:
                raise KeyboardInterrupt()
            break
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        raise KeyboardInterrupt()

    
if __name__ == "__main__":
    main()

    
    
