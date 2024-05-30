import yaml

import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class K8sPVCTest(rfm.RunOnlyRegressionTest):
    valid_systems = ['eidf:gpu-service']
    valid_prog_environs = ["*"]
    #k8s_config = "/home/eidf095/eidf095/crae-ml/epcc-reframe/tests/k8s/pvc_test.yml"
    
    bs = parameter(["4096K"])
    count = parameter([f"{1000}"])  # file_size = bs*count
    
    conversion ={
        "KB/s": 1e-6,
        "MB/s": 1e-3,
        "GB/s": 1,
        "TB/s": 1e3,
    }
    
    @run_after("init")
    def k8s_setup(self):
        k8s_config_path = "/".join(__file__.split("/")[:-1]) + "/pvc_test.yml"
        with open(k8s_config_path, "r") as stream:
            pod_info = yaml.safe_load(stream)
        pod_info["spec"]["template"]["spec"]["containers"][0]["args"][0] = pod_info["spec"]["template"]["spec"]["containers"][0]["args"][0].replace("BS", self.bs).replace("COUNT", self.count)
        print(pod_info["spec"]["template"]["spec"]["containers"][0]["args"][0])
        self.k8s_config = pod_info
    

    @performance_function("GB/s", perf_key="Read Speed")
    def get_read_speed(self):
        speed = sn.extractall(r"READ[\s\S]*?(\d+(\.\d+)? [KMGT]B/s)", self.stdout, 1, str)
        val, unit = str(speed[0]).split(" ")
        return round(float(val) * self.conversion[unit], 5)
    
    @performance_function("GB/s", perf_key="Write Speed")
    def get_write_speed(self):
        speed = sn.extractall(r"WRITE[\s\S]*?(\d+(\.\d+)? [KMGT]B/s)", self.stdout, 1, str)
        val, unit = str(speed[0]).split(" ")
        return round(float(val) * self.conversion[unit], 5)

    @sanity_function
    def assert_sanity(self):
        return sn.assert_found(r"WRITE", filename=self.stdout) and sn.assert_found(r"READ", filename=self.stdout) 
    
    @run_before("performance")
    def set_perf_variables(self):
        self.perf_variables = {
            "Read Speed": self.get_read_speed(),
            "Write Speed": self.get_write_speed(),
        }
