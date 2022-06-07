import reframe as rfm
import reframe.utility.sanity as sn

@rfm.parameterized_test(['libsci'],['mkl'])
class BlasTest(rfm.RegressionTest):
    def __init__(self, libname):
        self.valid_systems = ['archer2']
        self.valid_prog_environs = ['PrgEnv-gnu','PrgEnv-aocc']

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
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'performance','functionality','short'}

