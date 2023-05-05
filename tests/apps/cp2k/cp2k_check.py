import itertools
import os

import reframe as rfm
import reframe.utility.sanity as sn


class CP2KBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        #self.cpufreq = rfm.core.builtins.parameter(['1500000','2000000','2250000'])

        
        # Set Programming Environment 
        self.valid_prog_environs = ['PrgEnv-gnu']
        
        # Identify the executable
        self.executable = 'cp2k.psmp'

        # Output files to be retained
        self.keep_files = [output_file]

        # REGEX to extract key information from output file
        energy = sn.extractsingle(r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:'
                                  r'\s+(?P<energy>\S+)',
                                  output_file, 'energy', float)
        
        # Reference value to validate run with
        energy_reference = -870.934788


        # Sanity check to confirm test is correct
        self.sanity_patterns = sn.all([
            sn.assert_found('CP2K   ', output_file),
            sn.assert_reference(energy, energy_reference, -1.E-06, +1.0E-06)
        ])

        # REGEX to extract performance figures from test
        self.perf_patterns = {
            'perf': sn.extractsingle(r'\s+CP2K   '
                                     r'(\s+\S+){5}\s+(?P<perf>\S+)',
                                     output_file, 'perf', float)
        }

        self.maintainers = ['j.richings@epcc.ed.ac.uk']
        self.strict_check = False
        self.use_multithreading = False

        # Additional Slurm parameters. Requires adding to config file first.
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'applications','performance'}

# 2 Ghz test

@rfm.simple_test
class CP2KCPUCheck2GHz(CP2KBaseCheck):
    def __init__(self):
        super().__init__('cp2k.out')


        # Select system to use
        self.valid_systems = ['archer2:compute']
        
        # Description of test
        self.descr = 'CP2K check 2Ghz check'
        # Command line options for executable
        self.executable_opts = ('-i input_bulk_HFX_3.inp -o cp2k.out ').split()

        if (self.current_system.name in ['archer2']):
           # Which modules to load in test
           self.modules = ['cp2k']
           # Total number of tasks in slurm
           self.num_tasks = 384
           # Task per node in slurm
           self.num_tasks_per_node = 16
           # CPU's per task in slurm
           self.num_cpus_per_task = 8
           # Slurm job time limit
           self.time_limit = '1h'
           # Other Environment parameters to set
           self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                'OMP_PLACES': 'cores',
                'SLURM_CPU_FREQ_REQ': '2000000' 
                }
        # Performance test reference values
        self.reference = {
                'archer2:compute': {'perf': (335, 12, 'seconds'),
                }
            }
    
    # Additiona
    @run_before('run')
    def set_task_distribution(self):
        self.job.options = ['--distribution=block:block']

# 2.25 Ghz test  

@rfm.simple_test
class CP2KCPUCheck2_25GHz(CP2KBaseCheck):
    def __init__(self):
        super().__init__('cp2k.out')

        self.valid_systems = ['archer2:compute']
        self.descr = 'CP2K 2.25Ghz check'
        self.executable_opts = ('-i input_bulk_HFX_3.inp -o cp2k.out ').split()

        if (self.current_system.name in ['archer2']):
           self.modules = ['cp2k']
           self.num_tasks = 384
           self.num_tasks_per_node = 16
           self.num_cpus_per_task = 8
           self.time_limit = '1h'
           self.env_vars = {
                'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                'OMP_PLACES': 'cores',
                'SLURM_CPU_FREQ_REQ': '2250000'
                }

        self.reference = {
                'archer2:compute': {'perf': (250, -12, 12, 'seconds'),
                }
            }

    @run_before('run')
    def set_task_distribution(self):
        self.job.options = ['--distribution=block:block']

