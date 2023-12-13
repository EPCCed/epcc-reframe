import reframe as rfm
import reframe.utility.sanity as sn
from base import CosmoFlowBaseCheck

@rfm.simple_test
class CosmoFlowGPUBenchmark(CosmoFlowBaseCheck):
    valid_prog_environs = ["Default"]
    valid_systems = ['cirrus:compute-gpu-default']
    descr = "CosmoFlow GPU Benchmark"
    modules = ["openmpi/4.1.5-cuda-11.6"]
    num_tasks = None
    extra_resources = {
            "qos": {"qos": "gpu"},
            "gpu": {"num_gpus_per_node": "4"},
        }
    env_vars = {
            'OMP_NUM_THREADS': "5",
            "SRUN_CPUS_PER_TASK" : "5",
            "OMPI_MCA_mpi_warn_on_fork": "0",
            "PARAMS": '"--ntasks=32 --tasks-per-node=4"',
        }
    time_limit = "1h"
    
    prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', "conda activate mlperf-torch"]
    executable = "python"
    executable_opts = ["/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/train.py",
                            "--config", "/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/configs/cirrus_config.yaml",
                            "--device", "cuda"
    ]
    
    @run_before('run')
    def set_task_distribution(self):
        self.job.options = ["--nodes=8", "--exclusive"]  # make sure you change ntasks in PARAMS



    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        self.job.launcher.options.append("${PARAMS}")