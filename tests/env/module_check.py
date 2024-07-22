#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class DefaultPrgEnvCheck(rfm.RunOnlyRegressionTest):
    """Check the default compilers"""

    descr = "Ensure PrgEnv-cray is loaded by default"
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["Default"]
    executable = "module"
    executable_opts = ["-t", "list"]
    maintainers = ["a.turner@epcc.ed.ac.uk"]
    tags = {"production", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found(r"^PrgEnv-cray", self.stderr)


@rfm.simple_test
class DefaultModuleCheck(rfm.RunOnlyRegressionTest):
    """Check the default compilers"""

    descr = "Ensure epcc/setup-env is loaded by default"
    valid_prog_environs = ["Default"]
    valid_systems = ["cirrus:login"]
    executable = "module"
    executable_opts = ["-t", "list"]
    maintainers = ["e.broadway@epcc.ed.ac.uk"]

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found("setup-env", self.stdout)


@rfm.simple_test
class EnvironmentCheck(rfm.RunOnlyRegressionTest):
    """Check programming environemnts load correctly"""

    descr = "Ensure programming environment is loaded correctly"
    valid_systems = ["archer2:login", "cirrus:login"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc", "gcc", "intel"]

    executable = "module"
    executable_opts = ["-t", "list"]
    maintainers = ["Andy Turner"]
    tags = {"production"}

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        return sn.assert_found(self.current_environ.name, self.stderr)
