#!/usr/bin/env python3

"""Resnte50 CPU tests"""

import reframe as rfm

from resnet_base import ResNet50BaseCheck


@rfm.simple_test
class ResNet50CPUCheck(ResNet50BaseCheck):
    """Class for Resnet50 CPU benchmark"""

    descr = "ResNet50 CPU Benchmark"
    valid_systems = ["archer2:compute", "cirrus:compute"]
    num_task_per_node = 16
    executable = "python"
    num_tasks = 32
    time_limit = "12h"
    reference = {
        "archer2:compute": {
            "Throughput": (200, -0.05, 0.10, "images/s"),
            "Communication Time": (0.3, -0.1, 0.1, "s"),
            "Epoch Length": (500, -0.05, 0.05, "s"),
            "Total IO Time": (8.4, -0.1, 0.1, "s"),
        }
    }

    @run_after("init")
    def setup_systems(self):
        """Environment setup"""
        if self.current_system.name in ["archer2"]:
            self.valid_prog_environs = ["PrgEnv-gnu"]
            self.num_cpus_per_task = 8
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "SRUN_CPUS_PER_TASK": str(self.num_cpus_per_task),
            }
            self.prerun_cmds = [
                'eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"',
                "conda activate mlperf-torch-cpu",
            ]
            self.executable_opts = [
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py"
                " --config",
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/configs/archer2benchmark_config.yaml",
            ]

        elif self.current_system.name in ["cirrus"]:
            self.valid_prog_environs = ["Default"]
            self.modules = ["openmpi/4.1.5"]
            self.num_cpus_per_task = 36
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "OMPI_MCA_mpi_warn_on_fork": 0,
            }
            self.prerun_cmds = [
                'eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"',
                "conda activate mlperf-torch",
            ]
            self.executable_opts = [
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py",
                " --config",
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/configs/cirrusbenchmark_config.yaml",
            ]
