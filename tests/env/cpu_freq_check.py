#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CPUFreqTest(rfm.RunOnlyRegressionTest):
    """Checks that CPU frequency is set to 2GHz by default"""

    descr = "Checks whether SLURM_CPU_FREQ_REQ is set to 2GHz as default"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc"]
    executable = "./freq_print.sh"

    tags = {"production", "maintenance", "craype"}

    freq = 2000000

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU_CRAY_TARGET is set"""
        return sn.assert_found(f"SLURM_CPU_FREQ_REQ={self.freq}", self.stdout)


@rfm.simple_test
class CPUHighFreqTest(rfm.RunOnlyRegressionTest):
    """Checks that CPU frequency is set to 2.25GHz by default"""

    descr = "Checks whether SLURM_CPU_FREQ_REQ is set to 2GHz as default"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc"]
    executable = "./freq_print.sh"

    tags = {"production", "maintenance", "craype"}

    freq = 2250000

    @run_before('run')
    def set_cpu_freq(self):
        """Add slurm command line variable to job script to set frequency to 2.25Ghz"""
        self.job.launcher.options = ['--cpu-freq=2250000']

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU_CRAY_TARGET is set"""
        return sn.assert_found(f"SLURM_CPU_FREQ_REQ={self.freq}", self.stdout)
