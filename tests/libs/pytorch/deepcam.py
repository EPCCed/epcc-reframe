"""ReFrame tests for MLPerf HPC's DeepCAM"""

import os
import reframe as rfm

from mlperf_base import DeepCAMBase


@rfm.simple_test
class DeepCAMGPUtest(DeepCAMBase):
    """Running DeepCAM on GPU"""

    num_tasks = None
    num_nodes = 1
    num_gpus = 4
    num_gpus_per_node = 4
    time_limit = "1h"
    valid_systems = ["archer2:compute-gpu", "cirrus:compute-gpu"]
    valid_prog_environs = ["rocm-PrgEnv-cray", "Default"]
    reference = {
        "archer2:compute-gpu": {"epoch-time": (40, -0.1, 0.1, "s")},
        "cirrus:compute-gpu": {"epoch-time": (74, -0.1, 0.1, "s")},
    }

    @run_after("setup")
    def setup_job(self):
        """Set-up submission script"""
        train_script = os.path.join(self.mlperf_benchmarks.stagedir, "hpc", "deepcam", "src", "deepCam", "train.py")
        data_dir_prefix = " "
        local_batch_size = 1
        part = self.current_partition.fullname
        if part == "archer2:compute-gpu":
            data_dir_prefix = "/work/z19/shared/mlperf-hpc/deepcam/mini"
            local_batch_size = 8
            self.extra_resources = {
                "qos": {"qos": "gpu-exc"},
                "gpu": {"num_gpus_per_node": str(self.num_gpus)},
            }
        elif part == "cirrus:compute-gpu":
            self.modules = ["nvidia/cudnn/8.6.0-cuda-11.6"]
            data_dir_prefix = "/work/z19/shared/mlperf-hpc/deepcam/mini/"
            local_batch_size = 1
            self.extra_resources = {
                "qos": {"qos": "gpu"},
                "gpu": {"num_gpus_per_node": str(self.num_gpus)},
            }

        self.executable_opts = [
            train_script,
            "--wireup_method nccl-slurm",
            "--run_tag reframe-gpu",
            "--output_dir ${JOB_OUTPUT_PATH}",
            f"--data_dir_prefix {data_dir_prefix}",
            f"--local_batch_size {local_batch_size}",
            "--max_epochs 5",
        ]
        self.env_vars = {
            "OMP_NUM_THREADS": "1",
            "HOME": "${HOME/home/work}",
            "JOB_OUTPUT_PATH": "./results/${SLURM_JOB_ID}",
        }
        activate_pytorch = os.path.join(
            self.pytorch_env.stagedir, "reframe-mlperf-gpu", "reframe-mlperf-gpu", "bin", "activate"
        )
        self.prerun_cmds = [f"source {activate_pytorch}", "mkdir -p ${JOB_OUTPUT_PATH}/logs"]

    @run_before("run")
    def add_additional_options(self):
        """Add additional options to the job launcher"""
        self.job.launcher.options += [
            f"--ntasks={self.num_gpus}",
            f"--tasks-per-node={self.num_gpus_per_node}",
            "--hint=nomultithread",
        ]
        self.job.options = [f"--nodes={self.num_nodes}", "--exclusive"]


@rfm.simple_test
class DeepCAMCPUtest(DeepCAMBase):
    """Running DeepCAM on CPU"""

    num_nodes = 4
    num_tasks_per_node = 8
    num_cpus_per_task = 16
    num_tasks = 32
    time_limit = "1h"
    valid_systems = ["archer2:compute", "cirrus-ex:compute"]

    valid_prog_environs = ["PrgEnv-cray"]
    reference = {
        "archer2:compute": {"epoch-time": (272, -0.1, 0.1, "s")},
        "cirrus-ex:compute": {"epoch-time": (40, -0.1, 0.1, "s")},
    }
    
    @run_after("init")
    def set_modules(self):
        "Defined modules to load based on current system"
        if self.current_system.name in ["cirrus-ex"]:
            self.modules = ["py-torch"]

    @run_after("init")
    def set_num_tasks(self):
        "Set number of tasks based on current system"

        if self.current_system.name in ["cirrus-ex"]:
            self.num_tasks_per_node = 24
            self.num_cpus_per_task = 12

        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 8
            self.num_cpus_per_task = 16

        self.num_tasks = self.num_nodes * self.num_tasks_per_node

    @run_after("setup")
    def setup_job(self):
        """Set-up submission script"""
        train_script = os.path.join(self.mlperf_benchmarks.stagedir, "hpc", "deepcam", "src", "deepCam", "train.py")

        data_dir_prefix = None
        if self.current_system.name in ["cirrus-ex"]:
            data_dir_prefix = "/work/z19/shared/mlperf-hpc/deepcam/mini/"
        if self.current_system.name in ["archer2"]:
            data_dir_prefix = "/work/z19/shared/mlperf-hpc/deepcam/mini/"

        self.executable_opts = [
            train_script,
            "--wireup_method mpi",
            "--run_tag reframe-cpu",
            "--output_dir ${JOB_OUTPUT_PATH}",
            f"--data_dir_prefix {data_dir_prefix}",
            "--local_batch_size 1",
            "--max_inter_threads ${SLURM_CPUS_PER_TASK}",
            "--max_epochs 5",
            "--seed ${SLURM_JOB_ID}",
        ]

        self.env_vars = {
            "OMP_NUM_THREADS": "${SLURM_CPUS_PER_TASK}",
            "HOME": "${HOME/home/work}",
            "JOB_OUTPUT_PATH": "./results/${SLURM_JOB_ID}",
            "SRUN_CPUS_PER_TASK": "${SLURM_CPUS_PER_TASK}",
        }
        activate_pytorch = os.path.join(
            self.pytorch_env.stagedir, "reframe-mlperf-cpu", "reframe-mlperf-cpu", "bin", "activate"
        )
        self.prerun_cmds = [f"source {activate_pytorch}", "mkdir -p ${JOB_OUTPUT_PATH}/logs"]

    @run_before("run")
    def add_srun_options(self):
        """Add additional options to the job launcher"""
        self.job.launcher.options += [
            f"--ntasks={self.num_tasks}",
            f"--tasks-per-node={self.num_tasks_per_node}",
            "--hint=nomultithread",
        ]
