"""ReFrame base module for NAMD tests"""
import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.builtins import performance_function, sanity_function, run_after, run_before, variable


class NAMDBase(rfm.RunOnlyRegressionTest):
    """ReFrame base class for NAMD tests"""

    valid_prog_environs = ["intel", "nvidia-mpi"]
    executable = "namd2"

    maintainers = ["n.mannall@epcc.ed.ac.uk"]
    strict_check = True
    tags = {"applications", "performance"}

    extra_resources = {"qos": {"qos": "standard"}}

    input_file = variable(str)
    num_nodes = variable(int, value=1)

    cores = variable(
        dict,
        value={
            "archer2:compute": 128,
            "archer2-tds:compute": 128,
            "cirrus:compute": 36,
            "cirrus:compute-gpu": 40,
            "cirrus:highmem": 112,
        },
    )

    @run_after("setup")
    def setup_resources(self):
        if self.num_cpus_per_task > 1:
            self.modules = ["namd"]
            self.env_vars["OMP_NUM_THREADS"] = str(self.num_cpus_per_task)

            pemap = []
            commap = []
            for i in range(self.num_tasks_per_node):
                pemap.append(f"{self.num_cpus_per_task * i + 1}-{self.num_cpus_per_task * (i + 1) - 1}")
                commap.append(str(self.num_cpus_per_task * i))

            self.executable_opts = f"+setcpuaffinity +ppn {self.num_cpus_per_task - 1} +pemap {','.join(pemap)} +commap {','.join(commap)}".split()
        else:
            self.modules = ["namd/2.14-nosmp"]
            self.env_vars["OMP_NUM_THREADS"] = 1
        
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        

    @run_before("run", always_last=True)
    def set_input_file(self):
        self.executable_opts.append(self.input_file)

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"WallClock:\s+\S+\s+CPUTime:\s+\S+\s+Memory:\s+\S+\s+[MGT]B", self.stdout)

    @performance_function("kcal/mol", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"ENERGY:(\s+\S+\s+){10}\s+(?P<total_energy>\S+)\s+",
            self.stdout,
            "total_energy",
            float,
            item=-1,
        )

    @performance_function("ns/day", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return 1 / sn.extractsingle(
            r"Info: Benchmark time: \S+ CPUs \S+ s/step (?P<perf>\S+) days/ns",
            self.stdout,
            "perf",
            float,
            item=-1,
        )