#!/usr/bin/env python3
"""Reframe tests for CASTEP"""

import reframe as rfm
import reframe.utility.sanity as sn


class CASTEPBaseCheck(rfm.RunOnlyRegressionTest):
    """Base class for the CASTEP checks"""

    tags = {"applications", "performance"}
    valid_prog_environs = ["PrgEnv-gnu", "intel"]
    executable = "castep.mpi"

    maintainers = ["a.turner@epcc.ed.ac.uk"]
    strict_check = False
    use_multithreading = False
    extra_resources = {"qos": {"qos": "standard"}}

    output_file = "al3x3.castep"
    keep_files = [output_file]

    energy_reference = -77705.21093039

    reference = {
        "cirrus:compute": {"energy": (energy_reference, -0.01, 0.01, "eV")},
        "archer2:compute": {"energy": (energy_reference, -0.01, 0.01, "eV")},
    }

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Total time", self.keep_files[0])

    @performance_function("eV", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(r"Final energy, E\s+=\s+(?P<energy>\S+)", self.keep_files[0], "energy", float, item=-1)

    @performance_function("s", perf_key="runtime")
    def extract_runtime(self):
        """Extract total runtime to compare with reference value"""
        return (sn.extractsingle(r"Total time\s+=\s+(?P<runtime>\S+)", self.keep_files[0], "runtime", float),)

    @performance_function("s", perf_key="calctime")
    def extract_calctime(self):
        """Extract calctime to compare with reference value"""
        return (sn.extractsingle(r"Calculation time\s+=\s+(?P<calctime>\S+)", self.keep_files[0], "calctime", float),)


@rfm.simple_test
class CASTEPCPUCheck(CASTEPBaseCheck):
    """CASTEP Check for CPU"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    descr = "CASTEP corrctness and performance test"
    executable_opts = ["al3x3"]

    time_limit = "20m"
    num_cpus_per_task = 1
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    reference["archer2:compute"]["calctime"] = (126, -0.1, 0.1, "s")
    reference["archer2:compute"]["runtime"] = (132, -0.1, 0.1, "s")
    reference["cirrus:compute"]["calctime"] = (325.9, -1.65, 1.65, "s")
    reference["cirrus:compute"]["runtime"] = (328.2, -1.55, 1.55, "s")

    @run_after("init")
    def setup_environment(self):
        """Setup environment"""
        if self.current_system.name in ["archer2"]:
            self.modules = ["castep"]
            self.num_tasks = 512
            self.num_tasks_per_node = 128

        if self.current_system.name in ["cirrus"]:
            self.modules = ["castep/22.1.1"]
            self.num_tasks = 216
            self.num_tasks_per_node = 36
