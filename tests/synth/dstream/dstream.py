#!/usr/bin/env python3
"""
Distributed STREAM

Test that runs STREAM in parallel to measure memory performance of many-core
compute nodes. The code used is a modified version of DitributedStream from
https://github.com/adrianjhpc/DistributedStream which was originally written
by Adrian Jackson, EPCC. The modification removed the dependence on the MXML
library to provide a simpler test program
"""

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    """Stream test class"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["*"]
    build_system = "Make"
    executable = "distributed_streams"
    use_multithreading = False

    reference = {
        "archer2:compute": {
            "Copy": (208600, -0.05, 0.05, "MB/s"),
            "Scale": (199000, -0.05, 0.05, "MB/s"),
            "Add": (215700, -0.05, 0.05, "MB/s"),
            "Triad": (219400, -0.05, 0.05, "MB/s"),
        },
        "cirrus:compute": {
            "Copy": (88898, -0.05, 0.05, "MB/s"),
            "Scale": (84743, -0.05, 0.05, "MB/s"),
            "Add": (93845, -0.05, 0.05, "MB/s"),
            "Triad": (97291, -0.05, 0.05, "MB/s"),
        },
    }

    # System specific settings
    ntasks = {"archer2:compute": 128, "cirrus:compute": 36}
    ntasks_per_node = {"archer2:compute": 128, "cirrus:compute": 36}
    # These are the arguments to DistributedStream it
    #   arg1: number of elements in each array created. Should exceed the size of
    #         the highest cache level. (Arrays are double precision.)
    #   arg2: the number of repetitions of the benchmark

    # Cirrus L3 cache is 45 MiB

    args = {
        "archer2:compute": ["24000000", "1000"],
        "cirrus:compute": ["4500000", "1000"],
    }

    maintainers = ["a.turner@epcc.ed.ac.uk"]
    tags = {"performance", "short"}

    @performance_function("MB/s", perf_key="Copy")
    def extract_copy(self):
        """Extract copy performance value"""
        return sn.extractsingle(r"Node Copy:(\s+\S+:){2}\s+(?P<val>\S+):", self.stdout, "val", float, item=-1)

    @performance_function("MB/s", perf_key="Scale")
    def extract_scale(self):
        """Extract scale performance value"""
        return sn.extractsingle(r"Node Scale:(\s+\S+:){2}\s+(?P<val>\S+):", self.stdout, "val", float, item=-1)

    @performance_function("MB/s", perf_key="Add")
    def extract_add(self):
        """Extract add performance value"""
        return sn.extractsingle(r"Node Add:(\s+\S+:){2}\s+(?P<val>\S+):", self.stdout, "val", float, item=-1)

    @performance_function("MB/s", perf_key="Triad")
    def extract_triad(self):
        """Extract triad performance value"""
        return sn.extractsingle(r"Node Triad:(\s+\S+:){2}\s+(?P<val>\S+):", self.stdout, "val", float, item=-1)

    @sanity_function
    def assert_benchio(self):
        """Sanity checks"""
        return sn.assert_found(r"Node Triad", self.stdout)

    @run_before("run")
    def set_num_threads(self):
        """sets number of threads"""
        num_tasks = self.ntasks.get(self.current_partition.fullname, 1)
        self.num_tasks = num_tasks
        num_tasks_per_node = self.ntasks_per_node.get(self.current_partition.fullname, 1)
        self.num_tasks_per_node = num_tasks_per_node
        self.num_cpus_per_task = 1
        self.time_limit = "20m"
        args = self.args.get(self.current_partition.fullname, ["24000000", "10000"])
        self.extra_resources = {"qos": {"qos": "standard"}}
        self.executable_opts = args
