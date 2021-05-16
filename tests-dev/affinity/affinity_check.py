import reframe as rfm
import reframe.utility.sanity as sn

# Test process/thread affinity. Based on test from CSCS.

class AffinityTestBase(rfm.RegressionTest):
    def __init__(self, variant):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.sourcepath = 'xthi.c'
        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'basic'}

    @rfm.run_before('sanity')
    def set_sanity(self):

        def parse_cpus(x):
            return sorted(x)

        re_aff_cores = r'affinity = \s+(?P<cpus>[\d,]+\d)'
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


@rfm.parameterized_test(['omp_bind_threads'])
class AffinityOpenMPTest(AffinityTestBase):
    def __init__(self, variant):
        super().__init__(variant)
        self.descr = 'Checking the cpu affinity for OMP threads.'
        self.cases = {
            'omp_bind_threads': {
                'ref_archer2:compute': 'archer2_numa.txt',
                'num_cpus_per_task_archer2:compute': 16,
                'num_tasks': 8,
                'num_tasks_per_node': 8,
                'num_cpus_per_task': 16,
                'OMP_PLACES': 'cores',
            },
        }
        self.variant = variant
        self.num_tasks = self.cases[variant]['num_tasks']
        self.num_tasks_per_node = self.cases[variant]['num_tasks_per_node']
        self.num_cpus_per_task = self.cases[variant]['num_cpus_per_task']

    @rfm.run_before('run')
    def set_tasks_per_core(self):
        partname = self.current_partition.fullname
        self.num_cpus_per_task = self.cases[self.variant]['num_cpus_per_task:%s' % partname]
        self.num_tasks = 1
        self.variables  = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'OMP_PLACES': self.cases[self.variant]['OMP_PLACES']
        }


@rfm.parameterized_test(['fully_populated_nosmt'],
                        ['fully_populated_smt'],
                        ['single_process_per_numa'])
class SocketDistributionTest(AffinityTestBase):
    def __init__(self, variant):
        super().__init__(variant)
        self.descr = 'Checking distribution of processes to cores.'
        self.valid_systems = ['archer2:compute']
        self.cases = {
            'fully_populated_nosmt': {
                'ref_archer2:compute': 'archer2_fully_populated_nosmt.txt',
                'runopts_archer2:compute': ['--hint=nomultithread', '--distribution=block:block']
                'num_tasks': 128,
                'num_tasks_per_node': 128,
                'num_cpus_per_task': 1,
            },
            'fully_populated_smt': {
                'ref_archer2:compute': 'archer2_fully_populated_smt.txt',
                'runopts_archer2:compute': ['--hint=multithread', '--distribution=block:block']
                'num_tasks': 128,
                'num_tasks_per_node': 256,
                'num_cpus_per_task': 1,
            },
            'single_process_per_numa': {
                'ref_archer2:compute': 'archer2_single_process_per_numa.txt',
                'runopts_archer2:compute': ['--hint=nomultithread', '--distribution=block:block']
                'num_tasks': 8,
                'num_tasks_per_node': 8,
                'num_cpus_per_task': 16,
            },
        }
        self.num_tasks = self.cases[variant]['num_tasks']
        self.num_tasks_per_node = self.cases[variant]['num_tasks_per_node']
        self.num_cpus_per_task = self.cases[variant]['num_cpus_per_task']

    @rfm.run_before('run')
    def set_launcher(self):
        partname = self.current_partition.fullname
        self.job.launcher.options = self.cases[self.variant]['runopts_%s' % partname]

