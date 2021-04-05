import reframe as rfm
import reframe.utility.sanity as sn

@rfm.parameterized_test(['libsci'],['mkl'])
class BlasTest(rfm.RegressionTest):
    def __init__(self, libname):
        self.valid_systems = ['archer2']
        self.valid_prog_environs = ['gnu','amd']

        if libname == 'mkl':
            self.modules = ['mkl']
            self.prebuild_cmds = ['module load mkl']
        else:
            self.prebuild_cmds = []
        self.build_system = 'Make'
        self.build_system.makefile = f'Makefile.{libname}'

        self.executable = f'./dgemv_{libname}.x'
        self.executable_opts = ['3200','150','10000']

        self.sanity_patterns = sn.assert_found(r'Normal',
                                               self.stdout)

        self.perf_patterns = {
                'normal': sn.extractsingle(r'Normal\s+=\s+(?P<normal>\S+)',
                                     self.stdout, 'normal', float),
                'transpose': sn.extractsingle(r'Transpose\s+=\s+(?P<transpose>\S+)',
                                     self.stdout, 'transpose', float)
        }
        self.reference = {
                'archer2:compute': {'normal': (16.75, -0.15, 0.15, 'FLOP/s'),
                                    'transpose': (16.75, -0.15, 0.15, 'FLOP/s')},
                'archer2:login': {'normal': (16.75, -0.15, 0.15, 'FLOP/s'),
                                  'transpose': (16.75, -0.15, 0.15, 'FLOP/s')}
        }
        self.tags = {'performance','basic','numeric'}

    @rfm.run_before('compile')
    def setflags(self):
        if self.current_environ.name == 'gnu':
           self.prebuild_cmds.insert(0, 'module restore PrgEnv-gnu')
        elif self.current_environ.name == 'amd':
           self.prebuild_cmds.insert(0, 'module restore PrgEnv-aocc')

    @rfm.run_before('run')
    def setrunmodules(self):
        if self.current_environ.name == 'gnu':
           self.prerun_cmds = ['module load gcc']
        elif self.current_environ.name == 'amd':
           self.prerun_cmds = ['module load aocc']

