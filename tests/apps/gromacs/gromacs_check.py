import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class GromacsBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ['gnu']
        self.executable = 'gmx_mpi'

        self.keep_files = [output_file]

        energy = sn.extractsingle(r'\s+Potential\s+Kinetic En\.\s+Total Energy'
                                  r'\s+Conserved En\.\s+Temperature\n'
                                  r'(\s+\S+){2}\s+(?P<energy>\S+)(\s+\S+){2}\n'
                                  r'\s+Pressure \(bar\)\s+Constr\. rmsd',
                                  output_file, 'energy', float, item=-1)
        energy_reference = -12071400.0

        self.sanity_patterns = sn.all([
            sn.assert_found('Finished mdrun', output_file),
            sn.assert_reference(energy, energy_reference, -0.01, 0.01)
        ])

        self.perf_patterns = {
            'perf': sn.extractsingle(r'Performance:\s+(?P<perf>\S+)',
                                     output_file, 'perf', float)
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
class GromacsCPUCheck(GromacsBaseCheck):
    def __init__(self):
        super().__init__('md.log')

        self.valid_systems = ['archer2:compute']
        self.descr = 'GROMACS check'
        self.name = 'gromacs_cpu_check'
        self.executable_opts = ('mdrun -noconfout -s gmx_1400k_atoms.tpr ').split()

        if (self.current_system.name in ['archer2']):
           self.modules = ['gromacs']
           self.num_tasks = 512
           self.num_tasks_per_node = 128
           self.num_cpus_per_task = 1
           self.time_limit = '1h'
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        self.reference = {
                'archer2:compute': {'perf': (22.4, -0.1, 0.1, 'ns/day'),
            }
        }


