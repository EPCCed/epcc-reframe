# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.runtime import runtime


@rfm.simple_test
class DefaultPrgEnvCheck(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure PrgEnv-cray is loaded by default'
        self.valid_prog_environs = ['Default']
        self.valid_systems = ['archer2:login']
        self.executable = 'module'
        self.executable_opts = ['-t', 'list']
        self.maintainers = ['Andy Turner']
        self.tags = {'production', 'craype'}
        self.sanity_patterns = sn.assert_found(r'^PrgEnv-cray', self.stderr)


@rfm.simple_test
class DefaultModuleCheck(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure epcc/setup-env is loaded by default'
        self.valid_prog_environs = ['Default']
        self.valid_systems = ['cirrus:login']
        self.executable = 'module'
        self.executable_opts = ['-t', 'list']
        self.maintainers = ['Eleanor Broadway']
        self.sanity_patterns = sn.assert_found('setup-env', self.stdout)


@rfm.simple_test
class EnvironmentCheck(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure programming environment is loaded correctly'
        self.valid_systems = ['archer2:login']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu', 'PrgEnv-aocc']

        self.executable = 'module'
        self.executable_opts = ['-t', 'list']
        self.sanity_patterns = sn.assert_found(self.env_module_patt,self.stderr)
        self.maintainers = ['Andy Turner']
        self.tags = {'production', 'craype'}

    @property
    @deferrable
    def env_module_patt(self):
        return r'^%s' % self.current_environ.name

@rfm.simple_test
class EnvironmentCheckCirrus1(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure programming environment is loaded correctly'
        self.valid_systems = ['cirrus:login']
        self.valid_prog_environs = ['gnu']
        self.executable = 'module'
        self.executable_opts = ['-t', 'list']
        self.sanity_patterns = sn.assert_found('gcc', self.stdout)
        self.maintainers = ['Eleanor Broadway']
        self.tags = {'production'}

@rfm.simple_test
class EnvironmentCheckCirrus2(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure programming environment is loaded correctly'
        self.valid_systems = ['cirrus:login']
        self.valid_prog_environs = ['intel']
        self.executable = 'module'
        self.executable_opts = ['-t', 'list']
        self.sanity_patterns = sn.assert_found('intel', self.stdout)
        self.maintainers = ['Eleanor Broadway']
        self.tags = {'production'}
