"""ReFrame script for lammps dipole test"""

import os

import reframe as rfm
import reframe.utility.sanity as sn

from lammps_base import BuildLAMMPS, LAMMPSBase

class LAMMPSBaseExaalt(LAMMPSBase):
    """ReFrame LAMMPS Base class for Exaalt tests"""
    
    num_cpus_per_task = 1
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}
    modules = ["lammps"]
    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
            "cirrus-ex:compute" : 288
        },
    )

    reference = {
        "archer2:compute": {
            "energy": (-8.7467248, -0.001, 0.001, "kJ/mol"),
            "performance": (0.007, -0.1, None, "ns/day"),
        },
        "cirrus-ex:compute": {
            "performance": (0.055, -0.15, None, "ns/day"),
        },
    }


    @run_after("init")
    def setup_nnodes(self):
        """sets up number of nodes"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128

    @run_after("setup")
    def set_executable(self):
        """sets up executable"""
        self.executable = "lmp"

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)

    @performance_function("kJ/mol", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"^\s+100\s+\S+\s+\S+\s+\S+\s+(?P<energy>\S+)\s+\S+\s+$",
            self.keep_files[0],
            "energy",
            float,
            item=-1,
        )


@rfm.simple_test
class LAMMPSExaaltSmall(LAMMPSBaseExaalt):
    """ReFrame LAMMPS small test based on NERSC-10 Exaalt benchmark"""
    
    valid_systems = ["archer2:compute","cirrus-ex:compute"]
    descr = "Small performance test using NERSC-10 Exaalt LAMMPS benchmark reference run"
    tags = {"applications", "performance","small"}
    executable_opts = [
        "-in in.snap.test",
        "-var snapdir 2J8_W.SNAP",
        "-var nx 128",
        "-var ny 128",
        "-var nz 128",
        "-var nsteps 200",
    ]

    
    n_nodes = 4
    time_limit = "30m"

@rfm.simple_test
class LAMMPSExaaltRef(LAMMPSBaseExaalt):
    
    valid_systems = ["archer2:compute"]
    
    """ReFrame LAMMPS largescale test based on NERSC-10 Exaalt benchmark"""

    descr = "Largescale performance test using NERSC-10 Exaalt LAMMPS benchmark reference run"
    tags = {"largescale", "applications", "performance"}

    executable_opts = [
        "-in in.snap.test",
        "-var snapdir 2J8_W.SNAP",
        "-var nx 1024",
        "-var ny 1024",
        "-var nz 1024",
        "-var nsteps 100",
    ]

    n_nodes = 1024
    time_limit = "30m"
