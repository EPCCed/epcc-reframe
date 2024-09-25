#!/usr/bin/env python3

"""Reframe test for XCompact3D"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class XCompact3DHugeOFITest(rfm.RegressionTest):
    """XCompact 3D Huge Test"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"performance", "largescale", "applications"}

    num_nodes = 4096
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node * num_cpus_per_task

    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task), "MPICH_ALLTOALLV_THROTTLE": "32"}

    time_limit = "1h"
    build_system = "CMake"
    build_system.ftn = "ftn"
    prebuild_cmds = [
        "git clone https://github.com/xcompact3d/Incompact3d.git",
        "cd Incompact3d",
    ]
    builddir = "Incompact3d"
    executable = "Incompact3d/bin/xcompact3d"
    executable_opts = ["input-4096.i3d"]
    modules = ["cmake/3.29.4"]

    reference = {"archer2:compute": {"steptime": (6.3, -0.2, 0.2, "seconds")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Good job", self.stdout)

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"Averaged time per step \(s\):\s+(?P<steptime>\S+)",
            self.stdout,
            "steptime",
            float,
        )
