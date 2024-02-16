import reframe as rfm
import reframe.utility.sanity as sn

class CosmoFlowBaseCheck(rfm.RunOnlyRegressionTest):

    @performance_function("", perf_key="Delta Loss")
    def extract_delta_loss(self):
        return sn.extractsingle(r"Change In Train Loss at Epoch: (.*)", self.stdout, tag= 1, conv=float)
    
    @performance_function("inputs/s", perf_key="Throughput")
    def extract_throughput(self):
        return sn.extractsingle(r"Processing Speed: (.*)", self.stdout, tag= 1, conv=float)
    
    @performance_function("s", perf_key="Communication Time")
    def extract_communication(self):
        return sn.extractsingle(r"Communication Time: (.*)", self.stdout, tag= 1, conv=float)
    
    @performance_function("s", perf_key="Epoch Length")
    def extract_epoch_length(self):
        return sn.extractsingle(r"Time For Epoch: (.*)", self.stdout, tag= 1, conv=float)
    
    @performance_function("s", perf_key="Total IO Time")
    def extract_IO(self):
        return sn.extractsingle(r"Total IO Time: (.*)", self.stdout, tag= 1, conv=float)

    @sanity_function
    def assert_target_met(self):
        return sn.assert_found(r'Processing Speed', filename=self.stdout)
    
    @run_before("performance")
    def set_perf_variables(self):
        self.perf_variables = {
            "Throughput": self.extract_throughput(),
            "Epoch Length": self.extract_epoch_length(),
            "Delta Loss": self.extract_delta_loss(),
            "Communication Time": self.extract_communication(),
            "Total IO Time": self.extract_IO()
        }