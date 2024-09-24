#!/usr/bin/env python3

"""Resnet50 tests for graphcore"""

import reframe as rfm

from resnet_base import ResNet50BaseCheck


@rfm.simple_test
class ResNetGPUServiceGraphCoreBenchmark(ResNet50BaseCheck):
    """Resnet50 test class for graphcore"""

    valid_prog_environs = ["*"]
    valid_systems = ["eidf:graphcore"]
    context = "graphcore"
    k8s_resource = "ipujob"
