import reframe as rfm
import reframe.utility.sanity as sn


# Distributed STREAM
#
# Test that runs STREAM in parallel to measure memory performance of many-core
# compute nodes. The code used is a modified version of DitributedStream from
# https://github.com/adrianjhpc/DistributedStream which was originally written
# by Adrian Jackson, EPCC. The modification removed the dependence on the MXML
# library to provide a simpler test program
#


@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    def __init__(self):
        self.valid_systems = ['archer2:compute','cirrus:compute']
        self.valid_prog_environs = ['*']
        self.build_system = 'Make'
        self.executable = 'distributed_streams'
        self.use_multithreading = False
        self.sanity_patterns = sn.assert_found(r'Node Triad',
                                               self.stdout)
        self.perf_patterns = {
                'Copy': sn.extractsingle(r'Node Copy:(\s+\S+:){2}\s+(?P<val>\S+):',
                                     self.stdout, 'val', float, item=-1),
                'Scale': sn.extractsingle(r'Node Scale:(\s+\S+:){2}\s+(?P<val>\S+):',
                                     self.stdout, 'val', float, item=-1),
                'Add': sn.extractsingle(r'Node Add:(\s+\S+:){2}\s+(?P<val>\S+):',
                                     self.stdout, 'val', float, item=-1),
                'Triad': sn.extractsingle(r'Node Triad:(\s+\S+:){2}\s+(?P<val>\S+):',
                                     self.stdout, 'val', float, item=-1),
        }
        self.reference = {
            'archer2:compute': {
                'Copy':  (208600, -0.05, 0.05, 'MB/s'),
                'Scale': (199000, -0.05, 0.05, 'MB/s'),
                'Add':   (215700, -0.05, 0.05, 'MB/s'),
                'Triad': (219400, -0.05, 0.05, 'MB/s')
            },
            'cirrus:compute': {
                'Copy':  (88898, -0.05, 0.05, 'MB/s'),
                'Scale': (84743, -0.05, 0.05, 'MB/s'),
                'Add':   (93845, -0.05, 0.05, 'MB/s'),
                'Triad': (97291, -0.05, 0.05, 'MB/s'),
            }

        }

        # System specific settings
        self.ntasks = {
            'archer2:compute': 128,
            'cirrus:compute': 36
        }
        self.ntasks_per_node = {
            'archer2:compute': 128,
            'cirrus:compute': 36
        }
        # These are the arguments to DistributedStream itself:
        #   arg1: number of elements in each array created. Should exceed the size of
        #         the highest cache level. (Arrays are double precision.)
        #   arg2: the number of repetitions of the benchmark

        # Cirrus L3 cache is 45 MiB

        self.args = {
            'archer2:compute': ['24000000','1000'],
            'cirrus:compute': ['4500000','1000'],

        }

        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'performance','short'}

    @run_before('run')
    def set_num_threads(self):
        num_tasks = self.ntasks.get(self.current_partition.fullname, 1)
        self.num_tasks = num_tasks
        num_tasks_per_node = self.ntasks_per_node.get(self.current_partition.fullname, 1)
        self.num_tasks_per_node = num_tasks_per_node
        self.num_cpus_per_task = 1
        self.time_limit = '20m'
        args = self.args.get(self.current_partition.fullname, ['24000000','10000'])
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.executable_opts = args
