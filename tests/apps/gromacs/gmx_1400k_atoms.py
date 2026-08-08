#!/usr/bin/env python3

"""Gromacs 1400k atom HECBioSim benchmark"""

import reframe as rfm

from gromacs_base import GromacsBaseCheck



class Gromacs1400kAtomsBase(GromacsBaseCheck):
    """ReFrame GROMACS 14000k atoms test base class"""

    descr = "GROMACS 1400k performance"
    executable_opts = ("mdrun -noconfout -s gmx_1400k_atoms.tpr ").split()

    time_limit = "10m"

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
            "archer2-tds:compute": 128,
            "cirrus:compute": 36,
            "cirrus:compute-gpu": 40,
            "cirrus-ex:compute": 288,
        },
    )

    energy_reference = -12071400.0


    reference = {
        "archer2:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (24.0, -0.1, None, "ns/day"),
        },
        "archer2-tds:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (22.4, -0.1, None, "ns/day"),
        },
        "cirrus:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (5.50, -0.1, None, "ns/day"),
        },
        "cirrus:compute-gpu": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            "performance": (11.5, -0.05, None, "ns/day"),
        },
        "cirrus-ex:compute": {
            "energy": (energy_reference, -0.01, 0.01, "kJ/mol"),
            # The performance of this benchmark seems to be very variable, 
            # with performance sometimes dropping below 50 ns/day. 
            # Disabling the performance check for now until we can investigate this further.
            #"performance": (78.0, -0.1, None, "ns/day"), 
        },
    }

@rfm.simple_test
class GromacsCPUCheck(Gromacs1400kAtomsBase):
    """Gromacs CPU checks"""

    valid_systems = ["archer2:compute", "cirrus:compute","cirrus-ex:compute"]
    modules = ["gromacs"]
    descr = Gromacs1400kAtomsBase.descr + " -- CPU"

    n_nodes = 4

    num_cpus_per_task = 1
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    
    
    tags = {"applications", "performance", "small"}
    

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks_per_node = self.current_partition.processor.num_cpus
        self.num_tasks = self.n_nodes * self.num_tasks_per_node


@rfm.simple_test
class GromacsGPUCheck(Gromacs1400kAtomsBase):
    """Gromacs GPU checks"""

    valid_systems = ["cirrus:compute-gpu"]
    modules = ["gromacs/2023.4-gpu"]
    descr = Gromacs1400kAtomsBase.descr + " -- GPU"
    extra_resources = {
        "qos": {"qos": "short"},
        "gpu": {"num_gpus_per_node": "4"},
    }
    env_vars = {
        "OMP_NUM_THREADS": "1",
        "PARAMS": '"--ntasks=40 --tasks-per-node=40"',
    }
    
    n_nodes = 1
    num_tasks = None
    num_cpus_per_tasks = None

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        # Cirrus slurm demands it be done this way.
        # Trying to add $PARAMS directly to job.launcher.options fails.
        self.job.launcher.options.append("${PARAMS}")
