import reframe as rfm

from gromacs_base import GromacsBaseCheck


@rfm.simple_test
class GromacsGPUCheck(GromacsBaseCheck):
    def __init__(self):
        #  super().__init__("md.log")

        self.valid_systems = ["cirrus:compute-gpu"]
        self.descr = "GROMACS check GPU"
        self.extra_resources = {
            "qos": {"qos_id": "gpu"},
            "gpu": {"num_gpus_per_node": "4"},
        }
        self.executable_opts = (
            "mdrun -noconfout -s gmx_1400k_atoms.tpr "
        ).split()

        if self.current_system.name in ["cirrus"]:
            self.modules = ["gromacs/2022.3-gpu"]
            self.num_tasks = None
            #  self.num_tasks_per_node = 40
            #  self.num_cpus_per_task = 10
            self.time_limit = "1h"
        self.env_vars = {
            "OMP_NUM_THREADS": 1,
            "PARAMS": '"--ntasks=40 --tasks-per-node=40"',
        }

        self.reference["cirrus:compute-gpu"] = {
                "perf": (10.2, -0.05, 0.05, "ns/day"),
            }

    @run_before("run")
    def set_cpu_binding(self):
        self.job.launcher.options.append("${PARAMS}")
