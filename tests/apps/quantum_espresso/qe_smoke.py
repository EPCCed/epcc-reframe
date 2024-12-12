""" description """ 

import reframe as frm 
from qe_base import QEBase 

@rfm.simple_test 
class AUSURF112QESmall(QEBase):
    """ ReFrame QE short smoke test based on the AUSURF Benchmark inputs """

    valid_systems = ["archer2:compute","cirrus:compute"]
    modules = ["quantum_espresso"]
    descr = "ReFrame QE short smoke test based on the AUSURF Benchmark inputs"
    executable_opts = [
        "-i ausurf.in",
        "-o qe_ausurf.out"
    ]

    n_nodes = 1
    num_cpus_per_task = 1
    time_limit = "20m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)

    @run_after("init")
    def setup_nnodes(self):
        """sets up number of tasks per node"""
        if self.current_system.name in ["archer2"]:
            self.num_tasks_per_node = 128

    @run_before("run")
    def setup_resources(self):
        """sets up number of tasks"""
        self.num_tasks = self.n_nodes * self.cores.get(self.current_partition.fullname, 1)
