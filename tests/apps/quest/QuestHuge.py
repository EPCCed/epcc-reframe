#!/usr/bin/env python3

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class QuestQFTHugeTest(rfm.RegressionTest):
    """Quest Huge 4096 node Test"""

    valid_systems = ["archer2:compute-capability"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"performance", "largescale", "applications"}

    num_nodes = 4096
    num_tasks_per_node = 1
    num_cpus_per_task = 128
    num_tasks = num_nodes * num_tasks_per_node

    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task), "OMP_PLACES": "cores"}

    time_limit = "1hr"
    build_system = "Make"
    prebuild_cmds = [
        "git clone https://github.com/QuEST-Kit/QuEST.git",
        "source cmake_questQFT.sh qft",
    ]
    builddir = "build"
    executable = "build/qft"
    executable_opts = ["44"]
    modules = ["cmake/3.29.4"]

    @run_before("compile")
    def prepare_build(self):
        self.prebuild_cmd = ["git clone https://github.com/QuEST-Kit/QuEST.git .", "source cmake_questQFT.sh qft"]

    @run_before("run")
    def set_num_nodes(self):
        self.job.options = [f"--nodes={self.num_nodes}"]

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Total run time:", self.stdout)


# @performance_function("seconds", perf_key="performance")
# def extract_perf(self):
#     """Extract performance value to compare with reference value"""
#     return sn.extractsingle(
#         r"Averaged time per step \(s\):\s+(?P<steptime>\S+)",
#         self.stdout,
#         "time",
#         float,
#     )
