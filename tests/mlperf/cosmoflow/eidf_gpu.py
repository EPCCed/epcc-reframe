import os
import random
import string
import yaml
import copy

import reframe as rfm
import reframe.utility.sanity as sn

from cosmo_base import CosmoFlowBaseCheck

base_k8s_pod = {
    "apiVersion": "v1",
    "kind": "Pod",
    "metadata": {
        "name": "---CHANGE-NAME---"
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
                "env": [
                    {"name": "OMP_NUM_THREADS", "value": "4"}
                ],
                "resources": {
                    "requests": {
                        "cpu": 32,
                        "memory": "64Gi"
                    },
                    "limits": {
                        "cpu": 32,
                        "memory": "64Gi",
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
class CosmoFlowGPUServiceBenchmark(CosmoFlowBaseCheck):
    valid_prog_environs = ["*"]
    valid_systems = ['eidf:gpu-service']
    env_vars = {
        "KUBECONFIG":"/kubernetes/config"
    }
    
    executable = 'python'
    
    # num_gpus = parameter(1 << pow for pow in range(3))
    #num_gpus = variable(int, value=4) 
    num_gpus = parameter([4])
    lbs = parameter([8])
    
    #node_type = parameter(["NVIDIA-A100-SXM4-40GB", "NVIDIA-H100-80GB-HBM3"])
    node_type = parameter(["NVIDIA-A100-SXM4-40GB"])  

    @run_before("setup")
    def executable_setup(self):
        self.job_name = f"mlperf-cosmoflow"
        pod_info = copy.deepcopy(base_k8s_pod)
        pod_info["metadata"]["name"] = self.job_name
        pod_info["spec"]["containers"][0]["name"] = self.job_name[:-1] # remove '...-' at the end of str
        pod_info["spec"]["containers"][0]["workingDir"] = "/workspace/ML_HPC/CosmoFlow/Torch"
        pod_info["spec"]["containers"][0]["command"] = ["torchrun"]
        pod_info["spec"]["containers"][0]["args"] = [
            f"--nproc_per_node={self.num_gpus}", 
            "train.py", 
            "-lbs", f"{self.lbs}",
            "--device", "cuda",
            "-c", "/workspace/ML_HPC/CosmoFlow/Torch/config.yaml",
        ]
        
        pod_info["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] = self.num_gpus
        pod_info["spec"]["nodeSelector"]["nvidia.com/gpu.product"] = self.node_type
        pod_info["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"] = "cosmoflow-pvc"
        
        self.k8s_config = pod_info
        self.namespace = "eidf095ns"
        
    
    @performance_function("W", perf_key="Avg GPU Power Draw:")
    def extract_gpu_power_draw(self):
        return sn.extractsingle(r"Avg GPU Power Draw: (.*)", self.stdout, tag= 1, conv=float)
    
    @performance_function("%", perf_key="Avg GPU Utilization:")
    def extract_gpu_util(self):
        return sn.extractsingle(r"Avg GPU Utilization: (.*)", self.stdout, tag= 1, conv=float)

    @run_before("performance")
    def set_perf_variables(self):
        self.perf_variables = {
            "Throughput": self.extract_throughput(),
            "Epoch Length": self.extract_epoch_length(),
            "Delta Loss": self.extract_delta_loss(),
            "Communication Time": self.extract_communication(),
            "Avg GPU Power Draw": self.extract_gpu_power_draw(),
            "Avg GPU Utilization":self.extract_gpu_util(),
            "Total IO Time": self.extract_IO()
        }
        
        
        
        

    
    
    
    
    
