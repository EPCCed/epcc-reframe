import reframe.utility.sanity as sn
import reframe as rfm


@rfm.parameterized_test(['c'],['cpp'],['f90'])
class HelloTest(rfm.RegressionTest):
    def __init__(self, lang):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.sourcepath = f'hello.{lang}'
        self.sanity_patterns = sn.assert_found(r'Hello, World\!', self.stdout)

    @rfm.run_before('compile')
    def setenv(self):
        if self.current_environ.name == 'cray':
           self.prebuild_cmds = ['module restore PrgEnv-cray']
        elif self.current_environ.name == 'gnu':
           self.prebuild_cmds = ['module restore PrgEnv-gnu']
        elif self.current_environ.name == 'amd':
           self.prebuild_cmds = ['module restore PrgEnv-aocc']
