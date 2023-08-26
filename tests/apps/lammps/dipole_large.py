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

        energy = sn.extractsingle(r'Final energy, E\s+=\s+(?P<energy>\S+)',
                                  output_file, 'energy', float, item=-1)
        energy_reference = -77705.21093039

        self.sanity_patterns = sn.all([
            sn.assert_found('Total time', output_file),
            sn.assert_reference(energy, energy_reference, -0.01, 0.01)
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
        super().__init__('out.log')

        self.valid_systems = ['archer2:compute']
        self.descr = 'LAMMPS large scale performance test'
        self.executable_opts = ['in_2048.dipole']

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
