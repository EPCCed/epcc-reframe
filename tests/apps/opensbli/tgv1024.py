import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class OpenSBLIBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.executable = 'OpenSBLI_mpi_mp'

        self.sanity_patterns = sn.all([
            sn.assert_found('Time taken for 1 iteration', self.stdout),
        ])

        self.perf_patterns = {
            'time': sn.extractsingle(r'Time taken for 1 iteration,\s+(?P<time>\S+)',
                                     self.stdout, 'time', float),
        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.strict_check = False
        self.use_multithreading = False
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }

@rfm.simple_test
class OpenSBLIARCHER2LargeCheck(OpenSBLIBaseCheck):
    def __init__(self):

        self.valid_systems = ['archer2:compute']
        self.valid_prog_environs = ['PrgEnv-cray']
        self.descr = 'OpenSBLI large scale performance test'

        self.num_tasks = 128 * 1024
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = '20m'
        self.env_vars = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }
        
        self.reference = {
                'archer2:compute': {
                    'perf': (0.013, -0.3, 0.3, 's/iter'),
                }
        }
        self.tags = {'applications','performance','largescale'}
