import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.prebuild_cmds = [
            'wget http://www.cs.virginia.edu/stream/FTP/Code/stream.c',
        ]
        self.build_system = 'SingleSource'
        self.sourcepath = 'stream.c'
        self.build_system.cppflags = ['-DSTREAM_ARRAY_SIZE=$((1 << 25))']
        self.build_system.cflags = ['-fopenmp', '-O3', '-Wall']
        self.variables = {
            'OMP_NUM_THREADS': '4',
            'OMP_PLACES': 'cores'
        }
        self.sanity_patterns = sn.assert_found(r'Solution Validates',
                                               self.stdout)
        self.perf_patterns = {
            'Copy': sn.extractsingle(r'Copy:\s+(\S+)\s+.*',
                                     self.stdout, 1, float),
            'Scale': sn.extractsingle(r'Scale:\s+(\S+)\s+.*',
                                      self.stdout, 1, float),
            'Add': sn.extractsingle(r'Add:\s+(\S+)\s+.*',
                                    self.stdout, 1, float),
            'Triad': sn.extractsingle(r'Triad:\s+(\S+)\s+.*',
                                      self.stdout, 1, float)
        }
        self.reference = {
            'archer2': {
                'Copy':  (38350, -0.05, 0.05, 'MB/s'),
                'Scale': (24000, -0.05, 0.05, 'MB/s'),
                'Add':   (26000, -0.05, 0.05, 'MB/s'),
                'Triad': (26000, -0.05, 0.05, 'MB/s')
            }
        }
        # Flags per programming environment
        self.flags = {
            'cray':  ['-fopenmp', '-O3', '-Wall'],
            'gnu':   ['-fopenmp', '-O3', '-Wall']
        }

        # Number of cores for each system
        self.cores = {
            'archer2:login': 4,
            'archer2:compute': 8
        }

    @rfm.run_before('compile')
    def setflags(self):
        environ = self.current_environ.name
        self.build_system.cflags = self.flags.get(environ, [])

    @rfm.run_before('run')
    def set_num_threads(self):
        num_threads = self.cores.get(self.current_partition.fullname, 1)
        self.num_cpus_per_task = num_threads
        self.variables = {
            'OMP_NUM_THREADS': str(num_threads),
            'OMP_PLACES': 'cores'
        }
