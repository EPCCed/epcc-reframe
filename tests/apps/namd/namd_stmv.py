import reframe as rfm
from reframe.core.builtins import run_after, variable

from namd_base import NAMDBase


class NAMDStmvBase(NAMDBase):
    """ReFrame NAMD stmv (1M atoms) test base class"""

    valid_systems = ["cirrus:compute", "cirrus:highmem"]
    descr = "NAMD stmv (1M atoms) performance"
    input_file = "stmv.namd"
    time_limit = "10m"

    n_nodes = variable(
        dict,
        value={
            "archer2:compute": 4,
            "archer2-tds:compute": 4,
            "cirrus:compute": 4,
            "cirrus:compute-gpu": 1,
            "cirrus:highmem": 1,
        },
    )

    energy_reference = -2451791.8307

    reference = {
        "archer2:compute": {
            "energy": (energy_reference, -0.001, 0.001, "kcal/mol"),
        },
        "archer2-tds:compute": {
            "energy": (energy_reference, -0.001, 0.001, "kcal/mol"),
        },
        "cirrus:compute": {
            "energy": (energy_reference, -0.001, 0.001, "kcal/mol"),
        },
        "cirrus:highmem": {
            "energy": (energy_reference, -0.001, 0.001, "kcal/mol"),
        },
        "cirrus:compute-gpu": {
            "energy": (energy_reference, -0.001, 0.001, "kcal/mol"),
        },
    }


@rfm.simple_test
class NAMDStmvCPU(NAMDStmvBase):

    descr = NAMDStmvBase.descr + " -- CPU"

    cores_per_task = variable(
        dict,
        value={
            "archer2:compute": 16,
            "archer2-tds:compute": 16,
            "cirrus:compute": 18,
            "cirrus:highmem": 28,
        },
    )

    @run_after("setup")
    def setup_resources(self):
        self.num_cpus_per_task = self.cores_per_task.get(
            self.current_partition.fullname, 1
        )
        self.num_tasks_per_node = self.cores.get(
            self.current_partition.fullname, 1
        ) // self.num_cpus_per_task
        self.num_nodes = self.n_nodes.get(
            self.current_partition.fullname, 1
        )
        super().setup_resources()


@rfm.simple_test
class NAMDStmvCPUNoSMP(NAMDStmvBase):

    descr = NAMDStmvBase.descr + " -- CPU, No SMP"

    @run_after("setup")
    def setup_resources(self):
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = self.cores.get(
            self.current_partition.fullname, 1
        )
        self.num_nodes = self.n_nodes.get(
            self.current_partition.fullname, 1
        )
        super().setup_resources()


@rfm.simple_test
class NAMDStmvGPU(NAMDStmvCPU):
    valid_systems = ["cirrus:compute-gpu"]
    descr = NAMDStmvBase.descr + " -- GPU"

    extra_resources = {
        "qos": {"qos": "short"},
        "gpu": {"num_gpus_per_node": "4"},
    }

    cores_per_task = {
        "cirrus:compute-gpu": 10,
    }

    @run_after("setup")
    def setup_resources(self):
        super().setup_resources()
        self.modules = ["namd/2022.07.21-gpu"]
        devices = [str(i) for i in range(self.num_tasks_per_node)]
        self.executable_opts += ["+devices", ','.join(devices)]

        # Cannot specify tasks or CPUs as SBATCH options on the GPU partition.
        # CPUs are assigned based on the number of GPUs requested.
        self.job.launcher.options.append(
            f"--cpus-per-task={self.num_cpus_per_task} --ntasks={self.num_tasks} --tasks-per-node={self.num_tasks_per_node}"
        )
        self.num_cpus_per_task = None
        self.num_tasks = None
        self.num_tasks_per_node = None