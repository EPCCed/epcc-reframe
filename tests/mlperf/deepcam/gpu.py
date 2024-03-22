import reframe as rfm
import reframe.utility.sanity as sn
from base import DeepCamBaseCheck

@rfm.simple_test
class DeepCamGPUBenchmark(DeepCamBaseCheck):
    valid_prog_environs = ["Default", "rocm-PrgEnv-gnu"]
    valid_systems = ['cirrus:compute-gpu-default', "archer2:compute-gpu"]
    descr = "DeepCAM GPU Benchmark"
    modules = ["openmpi/4.1.6-cuda-11.6"]
    
    num_tasks = None
    num_gpus = parameter([4])  # parameter(1 << pow for pow in range(7))
    lbs = parameter([8])
    
    time_limit = "1h"

    extra_resources = {
            "qos": {"qos": "gpu"},
        }
    time_limit = "1h"
    env_vars = {
            'OMP_NUM_THREADS': "5",
            "SRUN_CPUS_PER_TASK" : "5",
            "OMPI_MCA_mpi_warn_on_fork": "0",
        }
    prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', 
                            "conda activate mlperf-torch", 
        ]
    executable = 'python'
    executable_opts = ["/work/z043/shared/chris-ml-intern//ML_HPC/DeepCAM/Torch/train.py",
                       " --config", "/work/z043/shared/chris-ml-intern/ML_HPC/DeepCAM/Torch/configs/cirrusbenchmark_config.yaml",
                       "--device", "cuda"
                        ]
    """ Have to Find Reference
    reference = {"cirrus:compute-gpu-default": {"Throughput": (1000, -0.05, 0.05, "images/s"),
                                     "Communication Time": (68, -0.1, 0.1, "s"),
                                     "Epoch Length": (100, -0.05, 0.05, "s"),
                                     "Total IO Time": (2, -0.5, 0.5, "s")  # Is supposed to be 50% not 5%
                                    }
                }
    """
    
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

       


