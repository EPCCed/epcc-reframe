import reframe as rfm
import reframe.utility.sanity as sn
from base import CosmoFlowBaseCheck

@rfm.simple_test
class CosmoFlowCPUCheck(CosmoFlowBaseCheck):
    valid_prog_environs = ['PrgEnv-gnu']
    descr = "CosmoFlow CPU Benchmark"
    valid_systems = ['archer2:compute', 'cirrus:compute']
    num_tasks = 32
    num_task_per_node=1
    time_limit = "1h"
    executable = 'python'

    @run_after("init")
    def setup_systems(self):
        if self.current_system.name in ["archer2"]:
            self.num_cpus_per_task = 128
            self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                "SRUN_CPUS_PER_TASK" : str(self.num_cpus_per_task)
            }
            self.prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', "conda activate mlperf-torch-rocm"]
            self.executable_opts = ["/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/train.py", 
                                    " --config", "/work/z04/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/configs/archer2_config.yaml"
                                    ]

            #self.reference = {"archer2:compute": {"Throughput": (200, -0.05, 0.10, "images/s"),
            #                                      "Communication Time": (295, -0.1, 0.1, "s")}
            #                 }

        elif self.current_system.name in ["cirrus"]:
            self.modules = ["openmpi/4.1.5"]
            self.num_cpus_per_task = 36

            self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                "SRUN_CPUS_PER_TASK" : str(self.num_cpus_per_task),
                "OMPI_MCA_mpi_warn_on_fork": 0
            }
            self.prerun_cmds = ['eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"', "conda activate mlperf-torch"]
            self.executable_opts = ["/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py",
                                    " --config", "/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/configs/cirrus_config.yaml"
                                    ]
    

    

    


