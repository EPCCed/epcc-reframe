import reframe as rfm
import reframe.utility.sanity as sn

# Test process/thread affinity. Based on test from CSCS.

class AffinityTestBase(rfm.RegressionTest):
    
    def __init__(self, variant):
        self.valid_systems = ['archer2:compute']
        self.valid_prog_environs = ['*']
        self.build_system = "SingleSource"
        self.build_system.cflags = ['-fopenmp']
        self.sourcepath = 'affinity.c'
        self.cflags = ['-fopenmp']
        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'functionality','short'}

    @run_before('sanity')
    def set_sanity(self):

        def parse_cpus(x):
            return sorted(x)

        re_aff_cores = r'affinity = \s+(?P<cpus>\d+:\d+:(?:[\d+,]*|[\d+-]*)\d+)'
        self.aff_cores = sn.extractall(
            re_aff_cores, self.stdout, 'cpus', parse_cpus)
        ref_key = 'ref_' + self.current_partition.fullname
        self.ref_cores = sn.extractall(
            re_aff_cores, self.cases[self.variant][ref_key],
            'cpus', parse_cpus)

        # Ranks and threads can be extracted into lists in order to compare
        # them since the affinity programm prints them in ascending order.
        self.sanity_patterns = sn.all([
            sn.assert_eq(sn.sorted(self.aff_cores), sn.sorted(self.ref_cores))
        ])


@rfm.simple_test
class AffinityOMPTest(AffinityTestBase):
    
    variant = parameter(['omp_bind_threads'])
    
    def __init__(self):
        super().__init__(self.variant)
        self.descr = 'Checking core affinity for OMP threads.'
        self.cases = {
            'omp_bind_threads': {
                'ref_archer2:compute': 'archer2_numa_omp.txt',
                'num_cpus_per_task_archer2:compute': 16,
                'num_tasks': 8,
                'num_tasks_per_node': 8,
                'num_cpus_per_task': 16,
                'OMP_PLACES': 'cores',
            },
        }
        self.num_tasks = self.cases[self.variant]['num_tasks']
        self.num_tasks_per_node = self.cases[self.variant]['num_tasks_per_node']
        self.num_cpus_per_task = self.cases[self.variant]['num_cpus_per_task']
        self.extra_resources = {'qos': {'qos': 'standard'}}

    @run_before('run')
    def set_tasks_per_core(self):
        partname = self.current_partition.fullname
        self.num_cpus_per_task = self.cases[self.variant]['num_cpus_per_task_%s' % partname]
        self.num_tasks = 1
        self.env_vars = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'OMP_PLACES': self.cases[self.variant]['OMP_PLACES']
        }


@rfm.simple_test
class AffinityMPITest(AffinityTestBase):

    variant = parameter(['fully_populated_nosmt','fully_populated_smt','single_process_per_numa'])

    def __init__(self):
        super().__init__(self.variant)
        self.descr = 'Checking core affinity for MPI processes.'
        self.valid_systems = ['archer2:compute']
        self.cases = {
            'fully_populated_nosmt': {
                'ref_archer2:compute': 'archer2_fully_populated_nosmt.txt',
                'runopts_archer2:compute': ['--hint=nomultithread', '--distribution=block:block'],
                'num_tasks': 128,
                'num_tasks_per_node': 128,
                'num_cpus_per_task': 1,
            },
            'fully_populated_smt': {
                'ref_archer2:compute': 'archer2_fully_populated_smt.txt',
                'runopts_archer2:compute': ['--ntasks=256', '--ntasks-per-node=256', '--hint=multithread', '--distribution=block:block'],
                'num_tasks': 128,
                'num_tasks_per_node': 128,
                'num_cpus_per_task': 1,
            },
            'single_process_per_numa': {
                'ref_archer2:compute': 'archer2_single_process_per_numa.txt',
                'runopts_archer2:compute': ['--hint=nomultithread', '--distribution=block:block'],
                'num_tasks': 8,
                'num_tasks_per_node': 8,
                'num_cpus_per_task': 16,
            },
        }
        self.num_tasks = self.cases[self.variant]['num_tasks']
        self.num_tasks_per_node = self.cases[self.variant]['num_tasks_per_node']
        self.num_cpus_per_task = self.cases[self.variant]['num_cpus_per_task']
        self.extra_resources = {'qos': {'qos': 'standard'}}

    @run_before('run')
    def set_launcher(self):
        partname = self.current_partition.fullname
        self.job.launcher.options = self.cases[self.variant]['runopts_%s' % partname]

