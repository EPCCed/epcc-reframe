import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import reframe.utility.osext as osext
import os

# IO500 I/O benchmark - https://io500.org/

@rfm.simple_test
class IO500BuildTest(rfm.CompileOnlyRegressionTest):
    '''Clone and build the IO500 source code.'''

    def __init__(self):
        self.descr = 'Clone and build the IO500 benchmark.'
        self.lang = ['c']
        self.valid_systems = ['archer2:login']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.build_system = 'CustomBuild'
        self.sourcesdir = 'https://github.com/IO500/io500.git'
        self.build_system.commands = ['./prepare.sh']

    @sanity_function
    def validate_build(self):
        return sn.assert_not_found('error', self.stderr)
