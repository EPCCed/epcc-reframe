#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CrayCPUTargetTest(rfm.RunOnlyRegressionTest):
    """Checks that CPU target is correctly set"""

    descr = "Checks whether CRAY_CPU_TARGET is set"
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc"]
    sourcesdir = None
    executable = "echo CRAY_CPU_TARGET=$CRAY_CPU_TARGET"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU_CRAY_TARGET is set"""
        return sn.assert_found(r"CRAY_CPU_TARGET=\S+", self.stdout)
