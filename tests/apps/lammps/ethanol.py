"""ReFrame script for LAMMPS ethanol test"""

import os

import reframe as rfm
import reframe.utility.sanity as sn

from lammps_base import BuildLAMMPS, LAMMPSBase


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
            "cirrus:compute-gpu": 40,
        },
    )

    ethanol_energy_reference = 537394.35

    reference = {
        "cirrus:compute-gpu": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (9.4, -0.05, None, "ns/day"),
        },
        "archer2:compute": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (11.250, -0.05, None, "ns/day"),
        },
        "cirrus-ex:compute": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (26, -0.1, None, "ns/day"),
        },
        "archer2-tds:compute": {
            "energy": (ethanol_energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (11.250, -0.05, None, "ns/day"),
        },
    }

    @performance_function("kJ/mol", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"\s+11000\s+\S+\s+\S+\s+(?P<energy>\S+)",
            self.keep_files[0],
            "energy",
            float,
            item=-1,
        )


class LAMMPSEthanolCPU(LAMMPSBaseEthanol):
    """ReFrame LAMMPS Ethanol test for performance checks"""

    descr = LAMMPSBaseEthanol.descr + " -- CPU"

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of tasks per node"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128
        else:
            if self.current_system.name in ["cirrus-ex"]:
                self.num_tasks_per_node = 288

    @run_after("setup")
    def set_executable(self):
        """sets up executable"""
        self.executable = os.path.join(self.stream_binary.build_system.builddir, "lmp")

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.num_tasks_per_node


@rfm.simple_test
class LAMMPSEthanolCPURunReframeBuild(LAMMPSEthanolCPU):
    """ReFrame LAMMPS Ethanol test for performance checks of the reframe-built executable"""

    valid_systems = ["archer2:compute"]
    descr = LAMMPSEthanolCPU.descr + ", reframe-bult-executable -- CPU"
    stream_binary = fixture(BuildLAMMPS, scope="environment")

    @run_after("setup")
    def set_executable(self):
        """sets up executable"""
        self.executable = os.path.join(self.stream_binary.build_system.builddir, "lmp")


@rfm.simple_test
class LAMMPSEthanolCPURunModule(LAMMPSEthanolCPU):
    """ReFrame LAMMPS Ethanol test for performance checks of the default lammps module"""

    valid_systems = ["archer2:compute", "cirrus-ex:compute"]
    descr = LAMMPSEthanolCPU.descr + ", default lammps module -- CPU"

    @run_after("setup")
    def set_executable(self):
        """sets up executable"""
        self.executable = "lmp"


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
            #  self.num_tasks_per_node = 40

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        self.env_vars["PARAMS"] = "--exclusive --ntasks=40 --tasks-per-node=40"
        # Cirru slurm demands it be done this way.
        # Trying to add $PARAMS directly to job.launcher.options fails.
        if self.current_system.name in ["cirrus"]:
            self.job.launcher.options.append("${PARAMS}")
