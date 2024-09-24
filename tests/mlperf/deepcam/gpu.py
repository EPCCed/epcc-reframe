#!/usr/bin/env python3

"""Deepcam tests for gpus"""

import reframe as rfm

from deepcam_base import DeepCamBaseCheck


@rfm.simple_test
class DeepCamGPUBenchmark(DeepCamBaseCheck):
    """Class for deepcam tests on gpus"""

    valid_prog_environs = ["Default", "rocm-PrgEnv-gnu"]
    valid_systems = ["cirrus:compute-gpu", "archer2:compute-gpu-torch"]
    descr = "Deepcam GPU Benchmark"

    num_tasks = None
    num_gpus = parameter([4])  # parameter(1 << pow for pow in range(7))
    lbs = parameter([8])

    time_limit = "1h"
    num_nodes = 1

    @run_after("init")
    def setup_systems(self):
        """Setup environment"""
        self.executable_opts = [
            "/work/z043/shared/chris-ml-intern/ML_HPC/DeepCAM/Torch/train.py",
            "--config",
            "/work/z043/shared/chris-ml-intern/ML_HPC/DeepCAM/Torch/configs/archer2benchmark_config.yaml",
            "--device",
            "cuda",
            "-lbs",
            f"{self.lbs}",
            # "--t_subset_size", "1024",
            # "--v_subset_size", "512"
        ]
        if self.current_system.name in ["archer2"]:
            self.executable = ""
            self.extra_resources = {
                "qos": {"qos": "gpu-exc"},
                "gpu": {"num_gpus_per_node": str(self.num_gpus)},
            }
            self.prerun_cmds = [
                'eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"',
                "conda activate mlperf-torch-rocm",
            ]
            self.env_vars = {
                "OMP_NUM_THREADS": "8",
                "LD_LIBRARY_PATH": "$CRAY_MPICH_ROOTDIR/gtl/lib/:$LD_LIBRARY_PATH",
                "LD_PRELOAD": "$CRAY_MPICH_ROOTDIR/gtl/lib/libmpi_gtl_hsa.so:$LD_PRELOAD",
                "HOME": "$PWD",
            }

        elif self.current_system.name in ["cirrus"]:
            self.executable = "python"
            self.extra_resources = {
                "qos": {"qos": "gpu"},
            }
            self.modules = ["openmpi/4.1.6-cuda-11.6"]
            self.prerun_cmds = [
                'eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"',
                "conda activate mlperf_torch",
            ]
            self.env_vars = {
                "OMP_NUM_THREADS": "5",
                "SRUN_CPUS_PER_TASK": "5",
                "OMPI_MCA_mpi_warn_on_fork": "0",
            }

    @run_before("run")
    def set_task_distribution(self):
        """Setup task distribution"""
        if self.num_gpus <= 4:
            self.num_nodes = 1
        else:
            if self.num_gpus / 4 - float(self.num_gpus // 4) == 0:
                self.num_nodes = self.num_gpus // 4
            else:
                self.num_nodes = self.num_nodes // 4 + 1

        if self.current_system.name in ["cirrus"]:
            self.job.options = [
                f"--nodes={self.num_nodes}",
                "--exclusive",
                f"--gres=gpu:{self.num_gpus if self.num_gpus <= 4 else 4}",
            ]  # make sure you change ntasks in PARAMS
        elif self.current_system.name in ["archer2"]:
            self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        if self.current_system.name in ["cirrus"]:
            self.job.launcher.options.append(
                f"--ntasks={self.num_gpus} --tasks-per-node={self.num_gpus if self.num_gpus <= 4 else 4}"
            )

    # ----------------------------------------------------------------------------
