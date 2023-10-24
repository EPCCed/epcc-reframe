"""GROMACS 1400k atoms test module"""
import reframe as rfm

from gromacs_base import GromacsBaseCheck


@rfm.simple_test
class Gromacs1400katomsCheck(GromacsBaseCheck):
    """GROMACS 1400k atoms regression test"""

    descr = "GROMACS check CPU"
    modules = ["gromacs/2022.3-gpu"]
    executable_opts = ("mdrun -noconfout -s gmx_1400k_atoms.tpr ").split()
    extra_resources = {
        "qos": {"qos": "gpu"},
        "gpu": {"num_gpus_per_node": "4"},
    }
    n_nodes = 1
    num_cpus_per_task = 1
    time_limit = "1h"
    valid_systems = ["cirrus:compute-gpu"]
    num_tasks = None

    env_vars = {
        "OMP_NUM_THREADS": str(num_cpus_per_task),
        "PARAMS": '"--ntasks=40 --tasks-per-node=40"',
    }

    energy_reference = -12071400.0

    reference = {
        "cirrus:compute-gpu": {
            "energy": (energy_reference, 0.01, 0.01, "kJ/mol"),
            "performance": (10.2, -0.05, 0.05, "ns/day"),
        },
    }

    @run_after("setup")
    def setup_gpu_options(self):
        """sets up different resources for gpu systems"""
        # Cirrus slurm demands it be done this way.
        # Trying to add $PARAMS directly to job.launcher.options fails.
        self.job.launcher.options.append("${PARAMS}")
