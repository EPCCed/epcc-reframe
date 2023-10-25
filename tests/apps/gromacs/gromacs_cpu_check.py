"""GROMACS 1400k atoms CPU test module"""
import reframe as rfm

from gromacs_base import GromacsBaseCheck


@rfm.simple_test
class Gromacs1400katomsCheckCPU(GromacsBaseCheck):
    """GROMACS 1400k atoms CPU regression test"""

    descr = "GROMACS check CPU"
    modules = ["gromacs"]
    executable_opts = ("mdrun -noconfout -s gmx_1400k_atoms.tpr ").split()
    extra_resources = {"qos": {"qos": "standard"}}
    n_nodes = 4
    num_cpus_per_task = 1
    time_limit = "1h"
    valid_systems = ["archer2:compute", "cirrus:compute"]

    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    energy_reference = -12071400.0

    reference = {
        "cirrus:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (3.21, -0.01, 0.01, "ns/day"),
        },
        "archer2:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (22.4, -0.1, 0.1, "ns/day"),
        },
        "archer2-tds:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
        },
    }

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
            "cirrus:compute": 36,
        },
    )

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of nodes"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128
        elif self.current_system.name in ["cirrus"]:
            self.num_tasks_per_node = 36

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(
            self.current_partition.fullname, 1
        )
