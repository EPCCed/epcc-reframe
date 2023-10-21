import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class ARCHER2BlasTest(rfm.RegressionTest):
    variant = parameter(['libsci', 'mkl'])

    def __init__(self):
        self.valid_systems = ['archer2']
        self.valid_prog_environs = ['PrgEnv-gnu','PrgEnv-aocc']

        if self.variant == 'mkl':
            self.modules = ['mkl']
            self.prebuild_cmds = ['module load mkl']
        else:
            self.prebuild_cmds = []
        self.build_system = 'Make'
        self.build_system.makefile = f'Makefile.{self.variant}'

        self.executable = f'./dgemv_{self.variant}.x'
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
        self.env_vars = {
                'SLURM_CPU_FREQ_REQ': '2250000'
        }
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'performance','functionality','short'}


@rfm.simple_test
class CirrusBlasTest(rfm.RegressionTest):
    variant = parameter(['mkl'])

    def __init__(self):
        self.valid_systems = ['cirrus']
        self.valid_prog_environs = ['gnu','intel']

        if self.variant == 'mkl':
            self.modules = ['intel-20.4/cmkl']
            self.prebuild_cmds = ['module load intel-20.4/cmkl']
        else:
            self.prebuild_cmds = []
        self.build_system = 'Make'

        if self.valid_systems == 'cirrus':
            self.build_system.makefile = f'Makefile.{self.variant}.{self.valid_prog_environs}.cirrus'
        else:
            self.build_system.makefile = f'Makefile.{self.variant}'

        self.executable = f'./dgemv_{self.variant}.x'
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
                'cirrus:compute': {'normal': (7.40, -0.25, 0.25, 'FLOP/s'),
                                    'transpose': (8.08, -0.33, 0.33, 'FLOP/s')},
                'cirrus:login': {'normal': (6.97, -0.1, 0.1, 'FLOP/s'),
                                  'transpose': (7.80, -0.1, 0.1, 'FLOP/s')}

        }
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'performance','functionality','short'}
