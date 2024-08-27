"""ReFrame script for lammps dipole test"""
import reframe as rfm

from lammps_base import LAMMPSBase


@rfm.simple_test
class ExaaltLammpsSmall(LAMMPSBase):
    """ReFrame LAMMPS small test based on NERSC-10 Exaalt benchmark"""

    valid_systems = ["archer2:compute"]
    modules = ["lammps"]
    descr = "Small performance test using NERSC-10 Exaalt LAMMPS benchmark reference run"
    executable_opts = [
        "-in in.snap.test",
        "-var snapdir 2J8_W.SNAP",
        "-var nx 256",
        "-var ny 256",
        "-var nz 256",
        "-var nsteps 100",
    ]

    n_nodes = 16
    num_cpus_per_task = 1
    time_limit = "15m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
        },
    )

    reference = {
        "archer2:compute": {
            "performance": (0.009, -0.1, 0.1, "ns/day"),
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
