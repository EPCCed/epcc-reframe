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
    num_gpus = variable(int, value=32) #parameter(1 << pow for pow in range(7))
    
    extra_resources = {
            "qos": {"qos": "gpu"},
        }
    env_vars = {
            'OMP_NUM_THREADS': "5",
            "SRUN_CPUS_PER_TASK" : "5",
            "OMPI_MCA_mpi_warn_on_fork": "0",
            "PARAMS": '"--ntasks=8 --tasks-per-node=4"',
        }
    time_limit = "6h"
    
    prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', "conda activate mlperf-torch"]
    executable = "python"
    executable_opts = ["/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/train.py",
                            "--config", "/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/configs/cirrus_config.yaml",
                            "--device", "cuda"
    ]
    
    @run_before('run')
    def set_task_distribution(self):
        if self.num_gpus <= 4:
            num_nodes = 1
        else:
            if self.num_gpus/4 - float(self.num_gpus//4) == 0:
                num_nodes = self.num_gpus//4
            else:
                num_nodes = num_nodes//4 + 1
        self.job.options = [f"--nodes={num_nodes}", "--exclusive", f"--gres=gpu:{self.num_gpus if self.num_gpus <= 4 else 4}"]  # make sure you change ntasks in PARAMS




    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        self.job.launcher.options.append(f'--ntasks={self.num_gpus} --tasks-per-node={self.num_gpus if self.num_gpus <= 4 else 4}')

