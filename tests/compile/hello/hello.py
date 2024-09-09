"""Compilation tests"""

import reframe as rfm
import reframe.utility.sanity as sn


class HelloTestBase(rfm.RegressionTest):
    """Base class for hello world tests"""

    lang = parameter(["c", "cpp", "f90"])
    tags = {"functionality", "short"}
    time_limit = "5m"
    maintainers = ["r.apostolo@epcc.ed.ac.uk"]

    @run_before("compile")
    def prepare(self):
        """sets source file name"""
        self.sourcepath = f"hello.{self.lang}"

    @sanity_function
    def assert_finished(self):
        """confirms code execution"""
        return sn.assert_found(r"Hello, World\!", self.stdout)


@rfm.simple_test
class HelloTestCPU(HelloTestBase):
    """CPU systems test class"""

    valid_systems = ["-gpu"]
    valid_prog_environs = ["-gpu"]
    extra_resources = {
        "qos": {"qos": "standard"},
    }


@rfm.simple_test
class HelloTestGPU(HelloTestBase):
    """GPU systems test class"""

    valid_systems = ["-torch"]
    valid_prog_environs = ["+gpu"]
    extra_resources = {
        "qos": {"qos": "gpu"},
        "gpu": {"num_gpus_per_node": "1"},
    }
    num_tasks = None
    num_cpus_per_task = None

    @run_after("setup")
    def setup_gpu_options(self):
        """Change qos for ARCHER2"""
        self.extra_resources["qos"]["qos"] = "gpu-shd"
