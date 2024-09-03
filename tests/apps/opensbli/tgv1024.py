#!/usr/bin/env python3

"""ReFrame test for OpenSBLI"""

import reframe as rfm
import reframe.utility.sanity as sn


class OpenSBLIBaseCheck(rfm.RunOnlyRegressionTest):
    """Base class for SBLI test"""

    executable = "./OpenSBLI_mpi_openmp"
    maintainers = ["a.turner@epcc.ed.ac.uk"]
    tags = {"applications", "performance", "largescale"}
    strict_check = False
    use_multithreading = False
    extra_resources = {"qos": {"qos": "standard"}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that job finished successfully"""
        return sn.assert_found("Time taken for 1 iteration", self.stdout)

    @performance_function("s/iter", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return (
            sn.extractsingle(
                r"Time taken for 1 iteration,\s+(?P<time>\S+)",
                self.stdout,
                "time",
                float,
            ),
        )


@rfm.simple_test
class OpenSBLIARCHER2LargeCheck(OpenSBLIBaseCheck):
    """Large scale OpenSBLI test"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    descr = "OpenSBLI large scale performance test"

    num_tasks_per_node = 128
    num_tasks = num_tasks_per_node * 1024
    num_cpus_per_task = 1
    time_limit = "30m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    reference = {"archer2:compute": {"performance": (0.013, -0.3, 0.3, "s/iter")}}
