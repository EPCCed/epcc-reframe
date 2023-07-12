import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class CASTEPBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ['PrgEnv-gnu','intel']
        self.executable = 'castep.mpi'

        self.keep_files = [output_file]

        energy = sn.extractsingle(r'Final energy, E\s+=\s+(?P<energy>\S+)',
                                  output_file, 'energy', float, item=-1)
        energy_reference = -77705.21093039

        self.sanity_patterns = sn.all([
            sn.assert_found('Total time', output_file),
            sn.assert_reference(energy, energy_reference, -1.0, 1.0)
        ])

        self.perf_patterns = {
            'runtime': sn.extractsingle(r'Total time\s+=\s+(?P<runtime>\S+)',
                                     output_file, 'runtime', float),

            'calctime': sn.extractsingle(r'Calculation time\s+=\s+(?P<calctime>\S+)',
                                     output_file, 'calctime', float)
        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.strict_check = False
        self.use_multithreading = False
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'applications','performance'}

@rfm.simple_test
class CASTEPCPUCheck(CASTEPBaseCheck):
    def __init__(self):
        super().__init__('al3x3.castep')

        self.valid_systems = ['archer2:compute','cirrus:compute']
        self.descr = 'CASTEP corrctness and performance test'
        self.executable_opts = ['al3x3']

        if (self.current_system.name in ['archer2']):
           self.modules = ['castep']
           self.num_tasks = 512
           self.num_tasks_per_node = 128
           self.num_cpus_per_task = 1
           self.time_limit = '20m'
        self.env_vars= {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        if (self.current_system.name in ['cirrus']):
           self.modules = ['castep/22.1.1']
           self.num_tasks = 216
           self.num_tasks_per_node = 36
           self.num_cpus_per_task = 1
           self.time_limit = '20m'
        self.env_vars= {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        self.reference = {
                'archer2:compute': {
                    'calctime': (126, -0.1, 0.1, 's'),
                    'runtime': (132, -0.1, 0.1, 's')
                },
                'cirrus:compute': {
                    'calctime': (325.9, -1.65, 1.65, 's'),
                    'runtime': (328.2, -1.55, 1.55, 's')
                }
        }
