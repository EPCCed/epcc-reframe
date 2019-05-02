import reframe as rfm
import reframe.utility.sanity as sn

class IMBBaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self, test_version):
        super().__init__()
        self.descr = 'IMB: %s' % test_version
        self.valid_systems = ['*']

        self.num_tasks = 288
        self.num_tasks_per_node = 36
        self.num_cpus_per_task = 1
        self.time_limit = (0, 20, 0)
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

        self.modules = ['imb/20190426-mpt']
        self.executable = 'IMB-MPI1'
        self.executable_opts = ['-mem', '1.2', '-npmin', str(self.num_tasks), test_version]

#        score = sn.extractsingle(r'TOTAL\s+(?P<score>\S+)',
#                                     output_file, 'score', float)

        self.sanity_patterns = sn.all([
            sn.assert_found('All processes entering MPI_Finalize', self.stdout),
        ])

#        self.perf_patterns = {
#            'perf': sn.extractsingle(r'TOTAL\s+(?P<score>\S+)',
#                                     output_file, 'score', float)
#        }

#        self.reference = {
#            'cirrus:compute_mpt': {
#                'perf': (8.8, -0.1, 0.1),
#            }
#        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'basic', 'production'}

@rfm.simple_test
class IMBAlltoallvTest(IMBBaseTest):
    def __init__(self):
        super().__init__('Alltoallv')
        self.valid_systems = ['cirrus:compute_mpt']
        self.valid_prog_environs = ['PrgEnv-gcc6-mpt']

