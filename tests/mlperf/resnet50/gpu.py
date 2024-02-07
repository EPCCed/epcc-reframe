import reframe as rfm
import reframe.utility.sanity as sn
from base import ResNet50BaseCheck

@rfm.simple_test
class ResNet50GPUBenchmark(ResNet50BaseCheck):
    valid_prog_environs = ["Default", "rocm-PrgEnv-gnu"]
    valid_systems = ['cirrus:compute-gpu-default', "archer2:compute-gpu"]
    descr = "ResNet50 GPU Benchmark"
    
    num_tasks = None
    num_gpus = variable(int, value=4)  # parameter(1 << pow for pow in range(7))
    
    time_limit = "1h"
    executable = 'python'
    executable_opts = ["/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py",
                                "--config", "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/configs/archer2benchmark_config.yaml",
                                "--device", "cuda",
                                "-lbs", "16",
                                "--t_subset_size", "1024",
                                "--v_subset_size", "256"  
        ]
    reference = {"cirrus:compute-gpu-default": {"Throughput": (1000, -0.05, 0.05, "images/s"),
                                     "Communication Time": (68, -0.1, 0.1, "s"),
                                     "Epoch Length": (100, -0.05, 0.05, "s"),
                                     "Total IO Time": (2, -0.5, 0.5, "s")  # Is supposed to be 50% not 5%
                                    }
                }

    @run_after("init")
    def setup_systems(self):
        if self.current_system.name in ["archer2"]:
            self.extra_resources = {
            "qos": {"qos": "gpu-exc"},
            "gpu": {"num_gpus_per_node": str(self.num_gpus)}
            }
            self.prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', 
                            "conda activate mlperf-torch-rocm", 
            ]  
            self.env_vars = {
                'OMP_NUM_THREADS': "8",
                "MPICH_GPU_SUPPORT_ENABLED":"1"
            }
        
        elif self.current_system.name in ["cirrus"]:
            self.extra_resources = {
            "qos": {"qos": "gpu"},
            }
            self.modules = ["openmpi/4.1.5-cuda-11.6"]
            self.prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', 
                            "conda activate mlperf-torch", 
            ]
            self.env_vars = {
                'OMP_NUM_THREADS': "5",
                "SRUN_CPUS_PER_TASK" : "5",
                "OMPI_MCA_mpi_warn_on_fork": "0",
            }
    
    @run_before('run')
    def set_task_distribution(self):
        if self.num_gpus <= 4:
            self.num_nodes = 1
        else:
            if self.num_gpus/4 - float(self.num_gpus//4) == 0:
                self.num_nodes = self.num_gpus//4
            else:
                self.num_nodes = self.num_nodes//4 + 1
        
        if self.current_system.name in ["cirrus"]:
            self.job.options = [f"--nodes={self.num_nodes}", "--exclusive", f"--gres=gpu:{self.num_gpus if self.num_gpus <= 4 else 4}"]  # make sure you change ntasks in PARAMS
        elif self.current_system.name in ["archer2"]:
            self.job.options = [f"--nodes={self.num_nodes}", f"--exclusive"]




    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        if self.current_system.name in ["cirrus"]:
            self.job.launcher.options.append(f'--ntasks={self.num_gpus} --tasks-per-node={self.num_gpus if self.num_gpus <= 4 else 4}')
        elif self.current_system.name in ["archer2"]:
            self.job.launcher.options.append(f'--ntasks={self.num_gpus} --cpus-per-task=8 --hint=nomultithread --distribution=block:block')

        
        
