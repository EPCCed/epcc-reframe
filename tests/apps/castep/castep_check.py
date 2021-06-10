import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class CASTEPBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ['gnu']
        self.executable = 'castep.mpi'

        self.keep_files = [output_file]

        energy = sn.extractsingle(r'Final energy, E\s+=\s+(?P<energy>\S+)',
                                  output_file, 'energy', float, item=-1)
        energy_reference = -77705.21093039

        self.sanity_patterns = sn.all([
            sn.assert_found('Total time', output_file),
            sn.assert_reference(energy, energy_reference, -0.01, 0.01)
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
            'switches': {
                'num_switches': 1
            }
        }
        self.tags = {'applications','performance'}

@rfm.simple_test
class CASTEPCPUCheck(CASTEPBaseCheck):
    def __init__(self):
        super().__init__('al3x3.castep')

        self.valid_systems = ['archer2:compute']
        self.descr = 'CASTEP corrctness and performance test'
        self.name = 'castep_cpu_check'
        self.executable_opts = ['al3x3']

        if (self.current_system.name in ['archer2']):
           self.modules = ['castep']
           self.num_tasks = 512
           self.num_tasks_per_node = 128
           self.num_cpus_per_task = 1
           self.time_limit = '20m'
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        self.reference = {
                'archer2:compute': {
                    'calctime': (126, -0.1, 0.1, 's'),
                    'runtime': (132, -0.1, 0.1, 's')
                }
        }


