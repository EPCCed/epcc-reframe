"""ReFrame base module for NAMD tests"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import performance_function, run_after, run_before, sanity_function, variable


class NAMDBase(rfm.RunOnlyRegressionTest):
    """ReFrame base class for NAMD tests"""

    valid_prog_environs = ["intel", "nvidia-mpi", "PrgEnv-cray"]
    modules = ["namd/2.14"]
    executable = "namd2"

    maintainers = ["n.mannall@epcc.ed.ac.uk"]
    strict_check = True
    tags = {"applications", "performance"}

    qos = variable(str, value="standard")

    input_file = variable(str)
    num_nodes = variable(int, value=1)

    num_cores_per_task = variable(dict, value={})

    @run_after("setup")
    def setup_resources(self):
        """setup resources"""
        self.num_cpus_per_task = self.num_cores_per_task[self.current_partition.fullname]
        self.num_tasks_per_node = self.current_partition.processor.num_cpus // self.num_cpus_per_task

        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.env_vars["OMP_NUM_THREADS"] = str(self.num_cpus_per_task)

        self.extra_resources["qos"] = {"qos": self.qos}

        pemap = []
        commap = []
        for i in range(self.num_tasks_per_node):
            pemap.append(f"{self.num_cpus_per_task * i + 1}-{self.num_cpus_per_task * (i + 1) - 1}")
            commap.append(str(self.num_cpus_per_task * i))

        self.executable_opts = (
            f"+setcpuaffinity +ppn {self.num_cpus_per_task - 1} "
            "+pemap {','.join(pemap)} +commap {','.join(commap)}".split()
        )

    @run_before("run", always_last=True)
    def set_input_file(self):
        """setup input file"""
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


class NAMDNoSMPMixin(rfm.RegressionMixin):
    """NAMD no SMP test"""

    @run_after("setup", always_last=True)
    def remove_smp(self):
        """remove smp"""
        self.modules = ["namd/2.14-nosmp"]

        proc = self.current_partition.processor
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = proc.num_cpus

        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.env_vars["OMP_NUM_THREADS"] = 1

        self.executable_opts = []


class NAMDGPUMixin(rfm.RegressionMixin):
    """NAMD GPU test"""

    gpus_per_node = variable(int)
    executable_opts = []

    @run_after("setup", always_last=True)
    def add_gpu_devices(self):
        """GPU devices"""
        self.modules = ["namd/2022.07.21-gpu"]

        devices = [str(i) for i in range(self.gpus_per_node)]
        self.executable_opts += ["+devices", ",".join(devices)]

        # Cannot specify tasks or CPUs as SBATCH options on the GPU partition.
        # CPUs are assigned based on the number of GPUs requested.
        self.job.launcher.options.append(
            f"--cpus-per-task={self.num_cpus_per_task} --ntasks={self.num_tasks} "
            f"--tasks-per-node={self.num_tasks_per_node}"
        )
        self.num_cpus_per_task = None
        self.num_tasks = None
        self.num_tasks_per_node = None

        self.extra_resources["gpu"] = {"num_gpus_per_node": self.gpus_per_node}
