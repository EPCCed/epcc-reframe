import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class CudaJodTest(rfm.RunOnlyRegressionTest):
    valid_systems = ['eidf:gpu-service']
    valid_prog_environs = ["*"]
    k8s_config = "/home/eidf095/eidf095/crae-ml/epcc-reframe/tests/k8s/cuda-job.yml"
    
    reference = {
        "eidf:gpu-service": {
            "Interactions per second": (250, -0.1, 0.1, "Iters/s"),
            "Flops": (7440, -0.1, 0.1, "GLOP/s"),
        }
    }
    
    @performance_function("Iters/s", perf_key="Interactions per second")
    def extract_interactions_per_second(self):
        return sn.extractsingle(r"= (\d+\.\d+) billion interactions per second", self.stdout, tag= 1, conv=float)
    
    @performance_function("GLOP/s", perf_key="Flops")
    def extract_gflops(self):
        return sn.extractsingle(r"= (\d+\.\d+) double-precision GFLOP/s", self.stdout, tag= 1, conv=float)
    
    @sanity_function
    def assert_sanity(self):
        num_messages = sn.len(sn.findall(r'double-precision GFLOP/s', filename=self.stdout))
        return sn.assert_eq(num_messages, 3)    
    
    @run_before("performance")
    def set_perf_variables(self):
        self.perf_variables = {
            "Interactions per second": self.extract_interactions_per_second(),
            "Flops": self.extract_gflops(),
        }