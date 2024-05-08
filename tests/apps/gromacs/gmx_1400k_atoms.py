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
        },
    )

    energy_reference = -12071400.0

    reference = {
        "archer2:compute": {
            "energy": (energy_reference, 0.01, 0.01, "kJ/mol")
        },
        "archer2-tds:compute": {
            "energy": (energy_reference, 0.01, 0.01, "kJ/mol")
        },
        "cirrus:compute": {
            "energy": (energy_reference, 0.01, 0.01, "kJ/mol"),
        },
        "cirrus:compute-gpu": {
            "energy": (energy_reference, 0.01, 0.01, "kJ/mol")
        },
    }


@rfm.simple_test
class GromacsCPUCheck(Gromacs1400kAtomsBase):
    valid_systems = ["archer2:compute", "cirrus:compute"]
    modules = ["gromacs"]
    descr = Gromacs1400kAtomsBase.descr + " -- CPU"

    n_nodes = 4
    num_tasks = 128
    num_cpus_per_task = 1
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    reference["archer2:compute"]["performance"] = (
        22.4,
        -0.1,
        0.1,
        "ns/day",
    )
    reference["archer2-tds:compute"]["performance"] = (
        22.4,
        -0.1,
        0.1,
        "ns/day",
    )
    reference["cirrus:compute"]["performance"] = (
        3.21,
        -0.01,
        0.01,
        "ns/day",
    )

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of tasks per node"""
        self.num_tasks_per_node = self.cores.get(
            self.current_partition.fullname, 1
        )

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(
            self.current_partition.fullname, 1
        )


@rfm.simple_test
class GromacsGPUCheck(Gromacs1400kAtomsBase):
    valid_systems = ["cirrus:compute-gpu"]
    modules = ["gromacs/2022.3-gpu"]
    descr = Gromacs1400kAtomsBase.descr + " -- GPU"
    extra_resources = {
        "qos": {"qos_id": "gpu"},
        "gpu": {"num_gpus_per_node": "4"},
    }
    env_vars = {
        "OMP_NUM_THREADS": "1",
        "PARAMS": '"--ntasks=40 --tasks-per-node=40"',
    }

    n_nodes = 1
    num_tasks = None
    num_cpus_per_tasks = None

    reference["cirrus:compute-gpu"]["perf"] = (
        10.2,
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
