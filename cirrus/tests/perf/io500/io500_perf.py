import reframe as rfm
import reframe.utility.sanity as sn

class IO5000BaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self, test_version):
        super().__init__()
        self.descr = 'IO-500: %s' % test_version
        self.valid_systems = ['*']

        self.executable = './io500_%s' % test_version

        self.num_tasks = 2
        self.num_tasks_per_node = 36
        self.num_cpus_per_task = 1
        self.time_limit = (1, 0, 0)
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'basic', 'production'}

@rfm.simple_test
class IO500MPTTest(IO500BaseTest):
    def __init__(self):
        super().__init__('mpt')
        self.valid_systems = ['cirrus:compute_mpt']
        self.valid_prog_environs = ['PrgEnv-gcc6-mpt']

