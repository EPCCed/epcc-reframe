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
        "cirrus:compute": {"energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")},
        "cirrus:compute-gpu": {"energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")},
        "archer2:compute": {"energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")},
        "archer2-tds:compute": {"energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol")},
    }


@rfm.simple_test
class LAMMPSEthanolCPU(LAMMPSBaseEthanol):
    """ReFrame LAMMPS Ethanol test for performance checks"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    descr = LAMMPSBaseEthanol.descr + " -- CPU"

    reference["archer2:compute"]["performance"] = (16.800, -0.05, None, "ns/day")
    reference["archer2-tds:compute"]["performance"] = (16.800, -0.05, None, "ns/day")
    reference["cirrus:compute"]["performance"] = (4.8, -0.05, None, "ns/day")

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
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)


@rfm.simple_test
class LAMMPSEthanolGPU(LAMMPSBaseEthanol):
    """ReFrame LAMMPS Ethanol test for performance checks"""

    valid_systems = ["cirrus:compute-gpu"]
    descr = LAMMPSBaseEthanol.descr + " -- GPU"
    modules = ["lammps-gpu"]
    extra_resources = {
        "gpu": {"num_gpus_per_node": "4"},
    }
    exclusive_access = True

    tags = LAMMPSBase.tags.union({"gpu"})
    n_nodes = 1
    num_tasks = None
    num_cpus_per_task = None

    reference["cirrus:compute-gpu"]["performance"] = (9.4, -0.05, None, "ns/day")

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of tasks per node"""
        # unfinished
        if self.current_system.name in ["archer2"]:
            # self.num_tasks_per_node = 32
            self.extra_resources["qos"] = {"qos": "gpu-exc"}
            self.executable_opts = LAMMPSBaseEthanol.executable_opts + [
                "-k on g 4 -sf kk -pk kokkos newton on neigh half"
            ]
        elif self.current_system.name in ["cirrus"]:
            self.executable_opts = LAMMPSBaseEthanol.executable_opts + ["-sf gpu -pk gpu 4"]
            self.extra_resources["qos"] = {"qos": "short"}
            self.num_tasks_per_node = 40

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        self.env_vars["PARAMS"] = (
            f'"--exclusive --ntasks={self.num_tasks_per_node} --tasks-per-node={self.num_tasks_per_node}"'
        )
        # Cirru slurm demands it be done this way.
        # Trying to add $PARAMS directly to job.launcher.options fails.
        if self.current_system.name in ["cirrus"]:
            self.job.launcher.options.append("${PARAMS}")
