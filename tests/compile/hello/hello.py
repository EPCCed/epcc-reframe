import reframe as rfm
import reframe.utility.sanity as sn


class HelloTestBase(rfm.RegressionTest):

    lang = parameter(["c", "cpp", "f90"])
    tags = {"functionality", "short"}
    time_limit = "5m"

    @run_before('compile')
    def prepare(self):
        self.sourcepath = f"hello.{self.lang}"

    @sanity_function
    def assert_finished(self):
        return sn.assert_found(r"Hello, World\!", self.stdout)


@rfm.simple_test
class HelloTestCPU(HelloTestBase):
    valid_systems = ["*"]
    valid_prog_environs = ["-gpu"]
    extra_resources = {
        "qos": {"qos": "standard"},
    }


@rfm.simple_test
class HelloTestGPU(HelloTestBase):
    valid_systems = ["+gpu"]
    valid_prog_environs = ["+gpu"]
    extra_resources = {
        "qos": {"qos": "gpu"},
        "gpu": {"num_gpus_per_node": "1"},
    }
    num_tasks = None
    num_cpus_per_task = None
