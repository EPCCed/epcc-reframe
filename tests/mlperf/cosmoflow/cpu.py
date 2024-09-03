#!/usr/bin/env python3
"""cosmoflow cpu tests"""

import reframe as rfm

from cosmo_base import CosmoFlowBaseCheck


@rfm.simple_test
class CosmoFlowCPUCheck(CosmoFlowBaseCheck):
    """Cosmoflow CPU test"""

    valid_prog_environs = ["PrgEnv-gnu"]
    descr = "CosmoFlow CPU Benchmark"
    valid_systems = ["archer2:compute", "cirrus:compute"]
    num_tasks = 32
    num_task_per_node = 16
    time_limit = "2h"
    executable = "python"

    @run_after("init")
    def setup_systems(self):
        """Setup test environment"""
        if self.current_system.name in ["archer2"]:
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
                "/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/train.py",
                " --config",
                "/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/configs/archer2_config.yaml",
            ]

        elif self.current_system.name in ["cirrus"]:
            self.modules = ["openmpi/4.1.5"]
            self.num_cpus_per_task = 36

            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "SRUN_CPUS_PER_TASK": str(self.num_cpus_per_task),
                "OMPI_MCA_mpi_warn_on_fork": 0,
            }
            self.prerun_cmds = [
                'eval "$(/work/z043/shared/miniconda3/bin/conda shell.bash hook)"',
                "conda activate mlperf-torch",
            ]
            self.executable_opts = [
                "/work/z043/shared/chris-ml-intern/ML/ResNet50/Torch/train.py",
                " --config",
                "/work/z043/shared/chris-ml-intern/ML_HPC/CosmoFlow/Torch/configs/cirrus_config.yaml",
            ]
