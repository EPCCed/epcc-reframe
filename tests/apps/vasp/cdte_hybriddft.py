"""ReFrame definition for CdTe exact exchange test"""
import reframe as rfm

from vasp_base import VASPBase

@rfm.simple_test
class VASPCdTe(VASPBase):
    """ReFrame VASP CdTe (exact exchange) test"""

    valid_systems = ["archer2:compute"]
    modules = ["vasp", "PrgEnv-gnu", "craype-network-ucx", "cray-mpich-ucx"]
    executable = "vasp_ncl"
    prerun_cmds = ["tar -xf CdTe_input.tar.gz"]
    descr = "VASP CdTe (exact exchange) test"

    n_nodes = 8
    num_cpus_per_task = 4
    time_limit = "1h"
    env_vars = {
        "OMP_NUM_THREADS": str(num_cpus_per_task),
        "SRUN_CPUS_PER_TASK": str(num_cpus_per_task)
    }

    cores = variable(
        dict,
        value={
            "archer2:compute": 32,
        },
    )

    reference = {
        "archer2:compute": {
            "perf": (6.0, None, None, "LOOP+/hour"),
        },
    }

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(
            self.current_partition.fullname, 1
        )
        self.num_tasks_per_node = self.cores.get(
            self.current_partition.fullname, 1
        )
