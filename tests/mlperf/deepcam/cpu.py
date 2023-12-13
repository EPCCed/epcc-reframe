import reframe as rfm
import reframe.utility.sanity as sn
from base import DeepCamBaseCheck

@rfm.simple_test
class DeepCamCPUCheck(DeepCamBaseCheck):
    descr = "DeepCam CPU Benchmark"
    valid_systems = ['archer2:compute', 'cirrus:compute']
    num_task_per_node=1
    executable = 'python'
    num_tasks = 32
    time_limit = "1h"
    reference = {"archer2:compute": {"Throughput": (200, -0.05, 0.10, "images/s"),
                                     "Communication Time": (0.3, -0.1, 0.1, "s"),
                                     "Epoch Length": (500, -0.05, 0.05, "s"),
                                     "Total IO Time": (8.4, -0.1, 0.1, "s")
                                    }
                }
    @run_after("init")
    def setup_systems(self):
        if self.current_system.name in ["archer2"]:
            self.valid_prog_environs = ['PrgEnv-gnu']
            self.num_cpus_per_task = 128
            self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                "SRUN_CPUS_PER_TASK" : str(self.num_cpus_per_task)
            }
            self.prerun_cmds = ['eval "$(/work/ta127/shared/miniconda3/bin/conda shell.bash hook)"', "conda activate mlperf-torch"]
            self.executable_opts = ["/work/ta127/shared/chris-ml-intern/ML_HPC/DeepCAM/Torch/train.py", 
                                    " --config", "/work/ta127/shared/chris-ml-intern/ML_HPC/DeepCAM/Torch/configs/archer2benchmark_config.yaml"
                                    ]


        elif self.current_system.name in ["cirrus"]:
            self.valid_prog_environs = ['Default']
            self.modules = ["openmpi/4.1.5"]
            self.num_cpus_per_task = 36
            self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                "OMPI_MCA_mpi_warn_on_fork": 0
            }
            self.prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', "conda activate mlperf-torch"]
            self.executable_opts = ["/work/z043/shared/chris-ml-intern//ML_HPC/DeepCAM/Torch/train.py",
                                    " --config", "/work/z043/shared/chris-ml-intern/ML_HPC/DeepCAM/Torch/configs/cirrusbenchmark_config.yaml"
                                    ]


