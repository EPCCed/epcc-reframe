#!/usr/bin/env python3

"""Resnet50 tests for EIDF system"""


import reframe as rfm
import reframe.utility.sanity as sn
import yaml

from resnet_base import ResNet50BaseCheck


@rfm.simple_test
class ResNetGPUServiceBenchmark(ResNet50BaseCheck):
    """Resnet50 EIDF benchmark"""

    valid_prog_environs = ["*"]
    valid_systems = ["eidf:gpu-service"]
    num_gpus = parameter([4])
    lbs = parameter([8])

    # node_type = parameter(["NVIDIA-A100-SXM4-40GB", "NVIDIA-H100-80GB-HBM3"])
    node_type = parameter(["NVIDIA-A100-SXM4-40GB"])

    # pod_config="/home/eidf095/eidf095/crae-ml/epcc-reframe/tests/mlperf/pod-mlperf-resnet-.yaml"
    pod_config = "test"

    @run_after("init")
    def executable_setup(self):
        """Setup environment"""
        jobname = "mlperf-resnet-"
        with open(
            "/".join(__file__.split("/")[:-1]) + "/base_pod.yaml", "r"
        ) as stream:
            pod_info = yaml.safe_load(stream)
        pod_info["metadata"]["generateName"] = jobname
        pod_info["spec"]["containers"][0]["name"] = jobname[
            :-1
        ]  # remove '...-' at the end of str
        pod_info["spec"]["containers"][0]["workingDir"] = "/workspace/ML"
        pod_info["spec"]["containers"][0]["args"] = [
            f"--nproc_per_node={self.num_gpus}",
            "/workspace/ML/ResNet50/Torch/train.py",
            "-lbs",
            f"{self.lbs}",
            "-c",
            "/workspace/ML/ResNet50/Torch/config.yaml",
            "--t_subset_size",
            "2048",
            "--v_subset_size",
            "512",
        ]
        pod_info["spec"]["containers"][0]["resources"]["limits"][
            "nvidia.com/gpu"
        ] = self.num_gpus
        pod_info["spec"]["nodeSelector"][
            "nvidia.com/gpu.product"
        ] = self.node_type
        pod_info["spec"]["volumes"][0]["persistentVolumeClaim"][
            "claimName"
        ] = "imagenet-pv"

        self.file = f"pod-{jobname}.yaml"
        self.k8s_config = pod_info

    @performance_function("W", perf_key="Avg GPU Power Draw:")
    def extract_gpu_power_draw(self):
        """Extracts gpu power draw"""
        return sn.extractsingle(
            r"Avg GPU Power Draw: (.*)", self.stdout, tag=1, conv=float
        )

    @run_before("performance")
    def set_perf_variables(self):
        self.perf_variables = {
            "Throughput": self.extract_throughput(),
            "Epoch Length": self.extract_epoch_length(),
            "Delta Loss": self.extract_delta_loss(),
            "Communication Time": self.extract_communication(),
            "Avg GPU Power Draw": self.extract_gpu_power_draw(),
            "Total IO Time": self.extract_IO(),
        }
