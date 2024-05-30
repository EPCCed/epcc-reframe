import os
import random
import string
import yaml
import copy

import reframe as rfm
import reframe.utility.sanity as sn

from deepcam_base import DeepCamBaseCheck

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
                "env": [
                    {"name": "OMP_NUM_THREADS", "value": "8"}
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
class DeepCAMGPUServiceBenchmark(DeepCamBaseCheck):
    valid_prog_environs = ["*"]
    valid_systems = ['eidf:gpu-service']
    
    # num_gpus = parameter(1 << pow for pow in range(3))
    #num_gpus = variable(int, value=4) 
    num_gpus = parameter([4])
    lbs = 1 #parameter([0])
    dataset = parameter(["mini"])
    
    #node_type = parameter(["NVIDIA-A100-SXM4-40GB", "NVIDIA-H100-80GB-HBM3"])
    node_type = parameter(["NVIDIA-A100-SXM4-40GB"])  

    @run_after("init")
    def executable_setup(self):
        self.job_name = f"mlperf-deepcam-"
        if self.dataset == "mini":
            dset_path = "/mnt/ceph_rbd/deepcam/mini/deepcam-data-n512"
            pvc = "deepcam-mini"
        elif self.dataset == "full":
            dset_path = "/mnt/ceph_rbd/gridftp-save/deepcam/All-Hist"
            pvc = "deepcam-pvc"
        else:
            raise ValueError(f"Dataset type '{self.dataset}' is not supported please select full|mini")
        pod_info = copy.deepcopy(base_k8s_pod)
        pod_info["metadata"]["generateName"] = self.job_name
        pod_info["spec"]["containers"][0]["name"] = self.job_name[:-1] # remove '...-' at the end of str
        pod_info["spec"]["containers"][0]["workingDir"] = "/workspace/ML_HPC/DeepCAM"
        pod_info["spec"]["containers"][0]["command"] = ["torchrun"]
        pod_info["spec"]["containers"][0]["args"] = [
            f"--nproc_per_node={self.num_gpus}", 
            "/workspace/ML_HPC/DeepCAM/Torch/train.py",
            "-lbs", f"{self.lbs}",
            "-c", "/workspace/ML_HPC/DeepCAM/Torch/config.yaml",
            "--data_dir", dset_path #"/mnt/ceph_rbd/deepcam/mini/deepcam-data-n512" #"/mnt/ceph_rbd/gridftp-save/deepcam/All-Hist", 
        ]
        #print(" ".join(pod_info["spec"]["containers"][0]["args"]))
        
        pod_info["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"] = self.num_gpus
        pod_info["spec"]["nodeSelector"]["nvidia.com/gpu.product"] = self.node_type
        pod_info["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"] = pvc
        
        self.k8s_config = pod_info

    
    @performance_function("W", perf_key="Avg GPU Power Draw:")
    def extract_gpu_power_draw(self):
        return sn.extractsingle(r"Avg GPU Power Draw: (.*)", self.stdout, tag= 1, conv=float)

    @run_before("performance")
    def set_perf_variables(self):
        self.perf_variables = {
            "Throughput": self.extract_throughput(),
            "Epoch Length": self.extract_epoch_length(),
            "Communication Time": self.extract_communication(),
            "Avg GPU Power Draw": self.extract_gpu_power_draw(),
            "Total IO Time": self.extract_IO()
        }
        
        
        
        

    
    
    
    
    
