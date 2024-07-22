#!/usr/bin/env python3
"""Reframe test to check that there are enough unused inodes in the filesystems"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class INodeCheckARCHER2(rfm.RunOnlyRegressionTest):
    """Checks the number of free inodes in each file system of ARCHER2"""

    filesystem = parameter(
        [
            "/mnt/lustre/a2fs-work1",
            "/mnt/lustre/a2fs-work2",
            "/mnt/lustre/a2fs-work3",
            "/mnt/lustre/a2fs-work4",
            "/mnt/lustre/a2fs-nvme",
        ]
    )

    descr = "Check number of free inodes"
    valid_prog_environs = ["PrgEnv-cray"]
    valid_systems = ["archer2:login"]
    maintainers = ["a.turner@epcc.ed.ac.uk"]
    tags = {"production"}
    executable = "lfs df -i"

    reference = {
        "archer2": {
            "MDT-0": (75, None, 0.0, "% inodes"),
            "MDT-1": (75, None, 0.0, "% inodes"),
        }
    }

    @run_after("init")
    def setup_executable_opts(self):
        """Sets up executable opts"""
        self.executable_opts = [self.filesystem]

    @sanity_function
    def validate_test(self):
        """Checks that command ran successfully"""
        return sn.assert_found("MDT:0", self.stdout) and sn.assert_found("MDT:1", self.stdout)

    @performance_function("% inodes", perf_key="MDT-0")
    def extract_mdt0(self):
        """Returns % used for MDT0"""
        totinode = sn.extractsingle(r"\S+MDT0000\S+\s+(\S+)\s+.*", self.stdout, 1, int)
        usedinode = sn.extractsingle(r"\S+MDT0000\S+\s+\S+\s+(\S+)\s+.*", self.stdout, 1, int)
        return sn.round(100.0 * usedinode / totinode, 2)

    @performance_function("% inodes", perf_key="MDT-1")
    def extract_mdt1(self):
        """Returns % used for MDT1"""
        totinode = sn.extractsingle(r"\S+MDT0001\S+\s+(\S+)\s+.*", self.stdout, 1, int)
        usedinode = sn.extractsingle(r"\S+MDT0001\S+\s+\S+\s+(\S+)\s+.*", self.stdout, 1, int)
        return sn.round(100.0 * usedinode / totinode, 2)


@rfm.simple_test
class INodeCheckCirrus(rfm.RunOnlyRegressionTest):
    """Checks the number of free inodes in each file system of Cirrus"""

    filesystem = parameter(["/mnt/lustre/e1000/"])

    reference = {
        "cirrus": {
            "MDT-0": (75, None, 0.0, "% inodes"),
        }
    }

    descr = "Check number of free inodes"
    valid_prog_environs = ["gnu"]
    valid_systems = ["cirrus:login"]
    executable = "lfs df -i"
    maintainers = ["a.turner@epcc.ed.ac.uk"]
    tags = {"production"}

    @run_after("init")
    def setup_executable_opts(self):
        """Sets up executable opts"""
        self.executable_opts = [self.filesystem]

    @sanity_function
    def validate_test(self):
        """Checks that command ran successfully"""
        return sn.assert_found("MDT:0", self.stdout)

    @performance_function("% inodes", perf_key="MDT-0")
    def extract_mdt0(self):
        """Returns % used for MDT0"""
        totinode = sn.extractsingle(r"\S+MDT0000\S+\s+(\S+)\s+.*", self.stdout, 1, int)
        usedinode = sn.extractsingle(r"\S+MDT0000\S+\s+\S+\s+(\S+)\s+.*", self.stdout, 1, int)
        return sn.round(100.0 * usedinode / totinode, 2)
