import os
import random
import string
import yaml

import reframe as rfm

base_k8s_pod = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
        "generateName": "---CHANGE-NAME---"
    },
    "spec": {
        "restartPolicy": "Never",
        "containers": [
            {
                "name": "---CHANGE-NAME---",
                "image": "bigballoon8/mlperf-epcc",
                "workingDir": "---PATH-WORKDIR---",
                "command": [
                    "---ADD-CMDs---"
                ],
                "args": [
                    "---ADD-ARGS---"
                ],
                "resources": {
                    "requests": {
                        "cpu": 16,
                        "memory": "16Gi"
                    },
                    "limits": {
                        "cpu": 16,
                        "memory": "32Gi",
                        "nvidia.com/gpu": "---CHANGE INT--"
                    }
                },
                "volumeMounts": [
                    {
                        "mountPath": "/mnt/ceph_rbd",
                        "name": "volume"
                    },
                    {
                        "mountPath": "/dev/shm",
                        "name": "devshm"
                    }
                ]
            }
        ],
        "nodeSelector": {
            "nvidia.com/gpu.product": "---CHANGE-NAME---"
        },
        "volumes": [
            {
                "name": "volume",
                "persistentVolumeClaim": {
                    "claimName": "---CHANGE-NAME---"
                }
            },
            {
                "name": "devshm",
                "emptyDir": {
                    "medium": "Memory"
                }
            }
        ]
    }
}

@rfm.simple_test
class DeepCAMServiceBenchmark(rfm.RunOnlyRegressionTest):
    valid_prog_environs = ["*"]
    valid_systems = ['*']
    env_vars = {
        "KUBECONFIG":"/kubernetes/config"
    }
    
    job_name = f"deepcam-resnet-{''.join(random.choices(string.ascii_lowercase, k=8))}-"
    
    executable = 'python'

    
    num_gpus = variable(int, value=2) #parameter(1 << pow for pow in range(4))
    node_type = variable(str, value="NVIDIA-A100-SXM4-40GB") #parameter(["NVIDIA-A100-SXM4-40GB", "NVIDIA-A100-SXM4-80GB"])

    @run_after("init")
    def executable_setup(self):
        
        pod_info = base_k8s_pod
        pod_info["metadata"]["generateName"] = self.job_name
        pod_info["spec"]["containers"][0]["name"] = self.job_name[:-1] # remove '...-' at the end of str
        pod_info["spec"]["containers"][0]["workingDir"] = "/mnt/ceph_rbd/chris-ml-intern/ML/DeepCAM/Torch"
        pod_info["spec"]["containers"][0]["command"] = ["torchrun"]
        pod_info["spec"]["containers"][0]["args"] = [
            f"--nproc_per_node={self.num_gpus}", "train.py", "-c", "/mnt/ceph_rbd/chris-ml-intern/ML/DeepCAM/Torch/config.yaml"
        ]
        pod_info["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] = self.num_gpus
        pod_info["spec"]["nodeSelector"]["nvidia.com/gpu.product"] = self.node_type
        pod_info["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"] = "imagenet-pv"
        
        self.file = f"pod-{self.num_gpus}-{pod_info['spec']['nodeSelector']['nvidia.com/gpu.product']}.yaml"
        with open(os.path.join(os.getcwd(), self.file), "w+") as stream:
            yaml.safe_dump(pod_info, stream)
        
        self.prerun_cmds = [
            'eval "$(/home/eidf095/eidf095/crae-ml/miniconda3/bin/conda shell.bash hook)"', 
            f"kubectl create -f {os.path.join(os.getcwd(), self.file)}"
        ]
        
        self.executable_opts = [
            f"{os.path.join(os.path.dirname(__file__), 'src', 'k8s_monitor.py')}",
            "--base_pod_name", self.job_name,
            "--namespace", "eidf095ns"
        ]
    
    @run_before("cleanup")
    def cleanup_pod_yaml(self):
        os.remove(os.path.join(os.getcwd(), self.file))
        

        
        
        
        

    
    
    
    
    