import reframe as rfm
import reframe.utility.sanity as sn


class HelloTestBase(rfm.RegressionTest):

    lang = parameter(["c", "cpp", "f90"])

    valid_prog_environs = ["*"]
    sourcepath = f"hello.{self.lang}"
    sanity_patterns = sn.assert_found(r"Hello, World\!", self.stdout)
    tags = {"functionality", "short"}


@rfm.simple_test
class HelloTestCPU(HelloTestBase):
    valid_systems = ["-gpu"]
    extra_resources = {
        "qos": {"qos": "standard"},
    }


@rfm.simple_test
class HelloTestCPU(HelloTestBase):
    valid_systems = ["+gpu"]
    extra_resources = {
        "qos": {"qos": "standard"},
        "gpu": {"num_gpus_per_node": "1"},
    }
    num_tasks = None
    num_cpus_per_task = None
