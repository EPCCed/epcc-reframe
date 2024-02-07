import reframe as rfm
import reframe.utility.sanity as sn
from base import ResNet50BaseCheck

@rfm.simple_test
class ResNet50CSXBenchmark(ResNet50BaseCheck):
    valid_prog_environs = ["Default"]
    valid_systems = ['CS-2:cs2']
    descr = "ResNet50 Cerebras WSE Benchmark"
    cpus_per_task=16
    num_csx = 1
    time_limit = "2h"

    prerun_cmds = [
        'eval "$(/home/z043/z043/crae-cs1/mlperf_cs2_pt/bin/conda shell.bash hook)"',
        "cd /home/z043/z043/crae-cs1/chris-ml-intern/cs2/ML/ResNet50"
    ]
    executable = 'python'
    executable_opts = ["train.py"]