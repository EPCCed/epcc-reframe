import reframe as rfm
import reframe.utility.sanity as sn

from resnet_base import ResNet50BaseCheck

@rfm.simple_test
class ResNetGPUServiceBenchmark(ResNet50BaseCheck):
    valid_prog_environs = ["*"]
    valid_systems = ['eidf:graphcore']
    context = "graphcore"
    k8s_resource = "ipujob"
    
    
