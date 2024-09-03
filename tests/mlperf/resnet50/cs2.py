#!/usr/bin/env python3

"""Resnet50 tests for CS2"""

import reframe as rfm

from resnet_base import ResNet50BaseCheck


@rfm.simple_test
class ResNet50CSXBenchmark(ResNet50BaseCheck):
    """Resnet50 benchmark for CS2"""

    valid_prog_environs = ["Default"]
    valid_systems = ["eidf:cs2"]
    descr = "ResNet50 Cerebras WSE Benchmark"
    cpus_per_task = 16
    num_csx = 1
    time_limit = "12h"

    prerun_cmds = [
        "source /home/z043/z043/crae-cs1/mlperf_cs2_pt/bin/activate",
        "cd /home/z043/z043/crae-cs1/chris-ml-intern/cs2/ML/ResNet50/",
    ]
    executable = "python"
    executable_opts = ["train.py"]
