import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class CP2KBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ['PrgEnv-gnu']
        self.executable = 'cp2k.psmp'

        self.keep_files = [output_file]

        energy = sn.extractsingle(r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:'
                                  r'\s+(?P<energy>\S+)',
                                  output_file, 'energy', float)
        energy_reference = -870.934788

        self.sanity_patterns = sn.all([
            sn.assert_found('CP2K   ', output_file),
            sn.assert_reference(energy, energy_reference, -1.E-06, +1.0E-06)
        ])

        self.perf_patterns = {
            'perf': sn.extractsingle(r'\s+CP2K   '
                                     r'(\s+\S+){5}\s+(?P<perf>\S+)',
                                     output_file, 'perf', float)
        }

        self.maintainers = ['h.judge@epcc.ed.ac.uk']
        self.strict_check = False
        self.use_multithreading = False
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'applications','performance'}


@rfm.simple_test
class CP2KCPUCheck(CP2KBaseCheck):
    def __init__(self):
        super().__init__('cp2k.out')

        self.valid_systems = ['archer2:compute']
        self.descr = 'CP2K check'
        self.name = 'cp2k_cpu_check'
        self.executable_opts = ('-i input_bulk_HFX_3.inp -o cp2k.out ').split()

        if (self.current_system.name in ['archer2']):
           self.modules = ['cp2k']
           self.num_tasks = 384
           self.num_tasks_per_node = 16
           self.num_cpus_per_task = 8
           self.time_limit = '1h'
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'OMP_PLACES': 'cores'
        }

        self.reference = {
                'archer2:compute': {'perf': (250, -12, 12, 'seconds'),
                }
            }
        
    @rfm.run_before('run')
    def set_task_distribution(self):
        self.job.options = ['--distribution=block:block']



