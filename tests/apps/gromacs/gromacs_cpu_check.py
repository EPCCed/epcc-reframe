import reframe as rfm
from gromacs_base import GromacsBaseCheck

@rfm.simple_test
class GromacsCPUCheck(GromacsBaseCheck):
    def __init__(self):
        super().__init__("md.log")

        self.valid_systems = ["archer2:compute", "cirrus:compute"]
        self.descr = "GROMACS check CPU"
        self.executable_opts = (
            "mdrun -noconfout -s gmx_1400k_atoms.tpr "
        ).split()

        if self.current_system.name in ["archer2"]:
            self.modules = ["gromacs"]
            self.num_tasks = 512
            self.num_tasks_per_node = 128
            self.num_cpus_per_task = 1
            self.time_limit = "1h"
        self.env_vars = {"OMP_NUM_THREADS": str(self.num_cpus_per_task)}

        if self.current_system.name in ["cirrus"]:
            self.modules = ["gromacs"]
            self.num_tasks = 72
            self.num_tasks_per_node = 36
            self.num_cpus_per_task = 1
            self.time_limit = "1h"
        self.env_vars = {"OMP_NUM_THREADS": str(self.num_cpus_per_task)}

        self.reference = {
            "archer2:compute": {
                "perf": (22.4, -0.1, 0.1, "ns/day"),
            },
            "cirrus:compute": {
                "perf": (3.21, -0.01, 0.01, "ns/day"),
            },
        }
