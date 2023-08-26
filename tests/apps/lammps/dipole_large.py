import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class LAMMPSBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ['PrgEnv-gnu']
        self.executable = 'lmp'

        self.keep_files = [output_file]


        self.sanity_patterns = sn.all([
            sn.assert_found('Total wall time', output_file)
        ])

        self.perf_patterns = {
            'perf': sn.extractsingle(r'Performance:\s+(?P<perf>\S+)',
                                     output_file, 'perf', float),
        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.strict_check = False
        self.use_multithreading = False
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'applications','performance','largescale'}

@rfm.simple_test
class LAMMPSARCHER2LargeCheck(LAMMPSBaseCheck):
    def __init__(self):
        super().__init__('log.lammps')

        self.valid_systems = ['archer2:compute']
        self.descr = 'LAMMPS large scale performance test'
        self.executable_opts = ['-i in_2048.dipole']

        self.modules = ['lammps']
        self.num_tasks = 128 * 1024
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = '20m'
        self.env_vars = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }
        
        self.reference = {
                'archer2:compute': {
                    'perf': (260000.0, -0.1, 0.1, 'tau/day'),
                }
        }
