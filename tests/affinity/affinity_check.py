#!/usr/bin/env python3

"""Test process/thread affinity. Based on test from CSCS."""

import reframe as rfm
import reframe.utility.sanity as sn


class AffinityTestBase(rfm.RegressionTest):
    """Base class for the affinity tests"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["*"]
    build_system = "SingleSource"
    sourcepath = "affinity.c"
    maintainers = ["a.turner@epcc.ed.ac.uk"]
    tags = {"functionality", "short"}
    aff_cores = None
    ref_cores = None

    @run_before("compile")
    def prepare_build(self):
        """Setup build environment"""
        self.build_system.cflags = ["-fopenmp"]

    @run_before("sanity")
    def set_sanity(self):
        """Extracts affinity results"""

        def parse_cpus(x):
            return sorted(x)

        re_aff_cores = r"affinity = \s+(?P<cpus>\d+:\d+:(?:[\d+,]*|[\d+-]*)\d+)"
        self.aff_cores = sn.extractall(re_aff_cores, self.stdout, "cpus", parse_cpus)
        ref_key = "ref_" + self.current_partition.fullname
        self.ref_cores = sn.extractall(re_aff_cores, self.cases[self.variant][ref_key], "cpus", parse_cpus)

        # Ranks and threads can be extracted into lists in order to compare
        # them since the affinity programm prints them in ascending order.
        self.sanity_patterns = sn.all([sn.assert_eq(sn.sorted(self.aff_cores), sn.sorted(self.ref_cores))])


@rfm.simple_test
class AffinityOMPTest(AffinityTestBase):
    """OMP bind threads test"""

    variant = parameter(["omp_bind_threads"])

    descr = "Checking core affinity for OMP threads."
    cases = {}

    @run_after("init")
    def setup_environment(self):
        """Setup environment"""
        if self.current_system.name in ["archer2"]:
            self.cases = {
                "omp_bind_threads": {
                    "ref_archer2:compute": "archer2_numa_omp.txt",
                    "num_cpus_per_task_archer2:compute": 16,
                    "num_tasks": 8,
                    "num_tasks_per_node": 8,
                    "num_cpus_per_task": 16,
                    "OMP_PLACES": "cores",
                },
            }
        # Each 18-core processor is a single NUMA region.
        if self.current_system.name in ["cirrus"]:
            self.cases = {
                "omp_bind_threads": {
                    "ref_cirrus:compute": "cirrus_numa_omp.txt",
                    "num_cpus_per_task_cirrus:compute": 18,
                    "num_tasks": 2,
                    "num_tasks_per_node": 2,
                    "num_cpus_per_task": 18,
                    "OMP_PLACES": "cores",
                },
            }
        self.num_tasks = self.cases[self.variant]["num_tasks"]
        self.num_tasks_per_node = self.cases[self.variant]["num_tasks_per_node"]
        self.num_cpus_per_task = self.cases[self.variant]["num_cpus_per_task"]
        self.extra_resources = {"qos": {"qos": "standard"}}

    @run_before("run")
    def set_tasks_per_core(self):
        """Setup tasks"""
        partname = self.current_partition.fullname
        self.num_cpus_per_task = self.cases[self.variant][f"num_cpus_per_task_{partname}"]
        self.num_tasks = 1
        self.env_vars = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task),
            "OMP_PLACES": self.cases[self.variant]["OMP_PLACES"],
        }


@rfm.simple_test
class AffinityMPITestARCHER2(AffinityTestBase):
    """MPI affinity test for ARCHER2"""

    variant = parameter(
        [
            "fully_populated_nosmt",
            "fully_populated_smt",
            "single_process_per_numa",
        ]
    )

    descr = "Checking core affinity for MPI processes."
    valid_systems = ["archer2:compute"]
    cases = {
        "fully_populated_nosmt": {
            "ref_archer2:compute": "archer2_fully_populated_nosmt.txt",
            "runopts_archer2:compute": [
                "--hint=nomultithread",
                "--distribution=block:block",
            ],
            "num_tasks": 128,
            "num_tasks_per_node": 128,
            "num_cpus_per_task": 1,
        },
        "fully_populated_smt": {
            "ref_archer2:compute": "archer2_fully_populated_smt.txt",
            "runopts_archer2:compute": [
                "--ntasks=256",
                "--ntasks-per-node=256",
                "--hint=multithread",
                "--distribution=block:block",
            ],
            "num_tasks": 128,
            "num_tasks_per_node": 128,
            "num_cpus_per_task": 1,
        },
        "single_process_per_numa": {
            "ref_archer2:compute": "archer2_single_process_per_numa.txt",
            "runopts_archer2:compute": [
                "--hint=nomultithread",
                "--distribution=block:block",
            ],
            "num_tasks": 8,
            "num_tasks_per_node": 8,
            "num_cpus_per_task": 16,
        },
    }

    @run_after("init")
    def setup_variant(self):
        """sets up variants"""
        self.num_tasks = self.cases[self.variant]["num_tasks"]
        self.num_tasks_per_node = self.cases[self.variant]["num_tasks_per_node"]
        self.num_cpus_per_task = self.cases[self.variant]["num_cpus_per_task"]
        self.extra_resources = {"qos": {"qos": "standard"}}

    @run_before("run")
    def set_launcher(self):
        """Sets launcher"""
        partname = self.current_partition.fullname
        self.job.launcher.options = self.cases[self.variant][f"runopts_{partname}"]


@rfm.simple_test
class AffinityMPITestCirrus(AffinityTestBase):
    """MPI affinity test for Cirrus"""

    variant = parameter(["fully_populated_nosmt"])

    descr = "Checking core affinity for MPI processes."
    valid_systems = ["cirrus:compute"]
    cases = {
        "fully_populated_nosmt": {
            "ref_cirrus:compute": "cirrus_fully_populated_nosmt.txt",
            "runopts_cirrus:compute": [
                "--hint=nomultithread",
                "--distribution=block:block",
            ],
            "num_tasks": 36,
            "num_tasks_per_node": 36,
            "num_cpus_per_task": 1,
        },
    }

    @run_after("init")
    def setup_variant(self):
        """sets up variants"""
        self.num_tasks = self.cases[self.variant]["num_tasks"]
        self.num_tasks_per_node = self.cases[self.variant]["num_tasks_per_node"]
        self.num_cpus_per_task = self.cases[self.variant]["num_cpus_per_task"]
        self.extra_resources = {"qos": {"qos": "standard"}}

    @run_before("run")
    def set_launcher(self):
        """Sets launcher"""
        partname = self.current_partition.fullname
        self.job.launcher.options = self.cases[self.variant][f"runopts_{partname}"]
