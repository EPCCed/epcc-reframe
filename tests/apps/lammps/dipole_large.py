#!/usr/bin/env python3
"""ReFrame script for lammps dipole test"""
import reframe as rfm

from lammps_base import LAMMPSBase


@rfm.simple_test
class LAMMPSDipole(LAMMPSBase):
    """ReFrame LAMMPS Dipole test for Slingshot reliability"""

    valid_systems = ["archer2:compute"]
    modules = ["lammps"]
    descr = "Slingshot reliability test using LAMMPS/Dipole"
    executable_opts = ["-i in_2048.dipole"]

    n_nodes = 1024
    num_cpus_per_task = 1
    time_limit = "20m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
        },
    )

    reference = {
        "archer2:compute": {
            "perf": (260000.0, -0.1, 0.1, "tau/day"),
        },
    }

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of nodes"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)
