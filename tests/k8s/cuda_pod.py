"""CUDA pod test"""

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CudaPodTest(rfm.RunOnlyRegressionTest):
    """CUDA pod test class"""

    # Could probably be merged with cuda_job using a base class

    valid_systems = ["eidf:gpu-service"]
    valid_prog_environs = ["*"]
    k8s_config = "/".join(__file__.split("/")[:-1]) + "/cuda-pod.yml"

    reference = {
        "eidf:gpu-service": {
            "Interactions per second": (250, -0.1, 0.1, "Iters/s"),
            "Flops": (7440, -0.1, 0.1, "GLOP/s"),
        }
    }

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
