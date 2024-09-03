#!/usr/bin/env python3
"""Reframe test to check that filesystems are mounted"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class FileSystemMountCheck(rfm.RunOnlyRegressionTest):
    """Checks that all filesystems are mounted"""

    descr = "Ensure ARCHER2 file systems are mounted - "
    maintainers = ["j.richings@epcc.ed.ac.uk"]
    valid_prog_environs = ["PrgEnv-cray"]
    valid_systems = ["archer2:login"]
    tags = {"production", "craype"}
    filesystem = parameter(["work1", "work2", "work3", "work4", "nvme"])

    @run_after("init")
    def setup_executable(self):
        """Sets up executable and description"""
        self.executable = f'[[ -d  /mnt/lustre/a2fs-{self.filesystem}/ ]] && echo "Success" '
        self.descr += f"{self.filesystem}"

    @sanity_function
    def assert_finished(self):
        """Sanity check that filesystem is mounted"""
        return sn.assert_found(r"Success", self.stdout)
