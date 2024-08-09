"""CUDA pod parameterized test"""

import reframe as rfm
import reframe.utility.sanity as sn
import yaml


@rfm.simple_test
class CudaPodParameterizedTest(rfm.RunOnlyRegressionTest):
    """CUDA pod test class"""

    valid_systems = ["eidf:gpu-service"]
    valid_prog_environs = ["*"]
    n_bodies = parameter([512000, 512000 * 2])
    k8s_config = None

    @run_after("init")
    def k8s_setup(self):
        """Setup k8s"""
        k8s_config_path = "/".join(__file__.split("/")[:-1]) + "/cuda-pod.yml"
        with open(k8s_config_path, "r") as stream:
            pod_info = yaml.safe_load(stream)
        pod_info["spec"]["containers"][0]["args"] = [
            "-benchmark",
            f"-numbodies={self.n_bodies}",
            "-fp64",
            "-fullscreen",
        ]
        self.k8s_config = pod_info

    @performance_function("Iters/s", perf_key="Interactions per second")
    def extract_interactions_per_second(self):
        """Extracts interactions performance value"""
        return sn.extractsingle(r"= (\d+\.\d+) billion interactions per second", self.stdout, tag=1, conv=float)

    @performance_function("GLOP/s", perf_key="Flops")
    def extract_gflops(self):
        """Extracts GFLOPs performance value"""
        return sn.extractsingle(r"= (\d+\.\d+) double-precision GFLOP/s", self.stdout, tag=1, conv=float)

    @sanity_function
    def assert_sanity(self):
        """Sanity checks"""
        return sn.assert_found(r"double-precision GFLOP/s", filename=self.stdout)

    @run_before("performance")
    def set_perf_variables(self):
        """Sets reference values"""
        # Possibly redundant
        self.perf_variables = {
            "Interactions per second": self.extract_interactions_per_second(),
            "Flops": self.extract_gflops(),
        }
