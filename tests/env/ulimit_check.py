#!/usr/bin/env python3
"""Reframe test to check that user limits are unlimited"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class UlimitCheck(rfm.RegressionTest):
    """Checks user limits"""

    descr = "Checking the output of ulimit -s in node."
    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc", "gcc", "intel"]
    sourcepath = "ulimit.c"
    ntasks = 1
    ntasks_per_node = 1
    time_limit = "1m"
    extra_resources = {"qos": {"qos": "standard"}}
    tags = {"production"}

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.all(
            [
                sn.assert_found(r"The soft limit is unlimited", self.stdout),
                sn.assert_found(r"The hard limit is unlimited", self.stdout),
            ]
        )
