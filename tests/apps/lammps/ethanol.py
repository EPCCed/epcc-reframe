"""ReFrame script for LAMMPS ethanol test"""

import reframe as rfm

from lammps_base import LAMMPSBase


class LAMMPSBaseEthanol(LAMMPSBase):
    """ReFrame LAMMPS Ethanol test base class"""

    modules = ["lammps"]
    descr = "LAMMPS Ethanol performance"
    executable_opts = ["-i in.ethanol"]

    n_nodes = 4
    num_cpus_per_task = 1
    time_limit = "20m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
            "archer2-tds:compute": 128,
            "cirrus:compute": 36,
            "cirrus:compute-gpu": 40,
        },
    )

    ethanol_energy_reference = 537394.35

    reference = {
        "cirrus:compute": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")
        },
        "cirrus:compute-gpu": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")
        },
        "archer2:compute": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")
        },
        "archer2-tds:compute": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")
        },
    }


@rfm.simple_test
class LAMMPSARCHER2EthanolCPU(LAMMPSBaseEthanol):
    """ReFrame LAMMPS Ethanol test for performance checks"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    descr = LAMMPSBaseEthanol.descr + " -- CPU"

    reference["archer2:compute"]["performance"] = (
        16.800,
        -0.05,
        0.05,
        "ns/day",
    )
    reference["archer2-tds:compute"]["performance"] = (
        1,
        -0.01,
        0.01,
        "ns/day",
    )
    reference["cirrus:compute"]["performance"] = (4.8, -0.05, 0.05, "ns/day")

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of tasks per node"""
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


@rfm.simple_test
class LAMMPSARCHER2EthanolGPU(LAMMPSBaseEthanol):
    """ReFrame LAMMPS Ethanol test for performance checks"""

    valid_systems = ["cirrus:compute-gpu"]
    descr = LAMMPSBaseEthanol.descr + " -- GPU"
    modules = ["lammps-gpu"]
    extra_resources = {
        "qos": {"qos": "short"},
        "gpu": {"num_gpus_per_node": "4"},
    }
    env_vars["PARAMS"] = '"--exclusive --ntasks=40 --tasks-per-node=40"'

    n_nodes = 1
    num_tasks = None
    num_cpus_per_task = None

    executable_opts = LAMMPSBaseEthanol.executable_opts + ["-sf gpu -pk gpu 4"]

    reference["cirrus:compute-gpu"]["performance"] = (
        9.4,
        -0.05,
        0.05,
        "ns/day",
    )

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        # Cirrus slurm demands it be done this way.
        # Trying to add $PARAMS directly to job.launcher.options fails.
        self.job.launcher.options.append("${PARAMS}")
