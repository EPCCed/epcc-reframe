#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CrayCountersEnergyTest(rfm.RunOnlyRegressionTest):
    """Checks that the Node Energy counter is reporting"""

    descr = "Checks whether the node energy pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/energy"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that Energy is reported"""
        return sn.assert_found(r"\S+ J \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersPowerTest(rfm.RunOnlyRegressionTest):
    """Checks that the Node Power counter is reporting"""

    descr = "Checks whether the node power pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/power"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that Power is reporting"""
        return sn.assert_found(r"\S+ W \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersCPUEnergyTest(rfm.RunOnlyRegressionTest):
    """Checks that the CPU Energy counter is reporting"""

    descr = "Checks whether the cpu energy pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/cpu_energy"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU Energy is reporting"""
        return sn.assert_found(r"\S+ J \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersCPUPowerTest(rfm.RunOnlyRegressionTest):
    """Checks that the CPU Power counter is reporting"""

    descr = "Checks whether the cpu power pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/cpu_power"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU Power is reporting"""
        return sn.assert_found(r"\S+ W \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersMemoryEnergyTest(rfm.RunOnlyRegressionTest):
    """Checks that the Memory Energy counter is reporting"""

    descr = "Checks whether the memory energy pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/memory_energy"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that Memory Energy is reporting"""
        return sn.assert_found(r"\S+ J \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersMemPowerTest(rfm.RunOnlyRegressionTest):
    """Checks that the Memory Power counter is reporting"""

    descr = "Checks whether the memory power pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/memory_power"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that Memory Power is reporting"""
        return sn.assert_found(r"\S+ W \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersCPU0TempTest(rfm.RunOnlyRegressionTest):
    """Checks that the CPU 0 Temperature counter is reporting"""

    descr = "Checks whether the cpu 0 temperature pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/cpu0_temp"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU 0 temperature is reporting"""
        return sn.assert_found(r"\S+ C \S+ us", self.stdout)


@rfm.simple_test
class CrayCountersCPU1TempTest(rfm.RunOnlyRegressionTest):
    """Checks that the CPU 1 Temperature counter is reporting"""

    descr = "Checks whether the cpu 1 temperature pm counter is accessible and reporting"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    sourcesdir = None
    executable = "cat /sys/cray/pm_counters/cpu1_temp"

    tags = {"production", "maintenance", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that CPU 1 temperature is reporting"""
        return sn.assert_found(r"\S+ C \S+ us", self.stdout)
