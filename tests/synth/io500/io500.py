import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
import reframe.utility.osext as osext
from reframe.core.backends import getlauncher
import os

# IO500 I/O benchmark - https://io500.org/

# Build the IO500 application from source.
# This is a dependency of the run tests below.
@rfm.simple_test
class IO500BuildTest(rfm.CompileOnlyRegressionTest):
    '''Clone and build the IO500 source code.'''

    descr = 'Clone and build the IO500 benchmark.'
    lang = ['c']
    valid_systems = ['archer2:compute']
    valid_prog_environs = ['PrgEnv-gnu']
    build_system = 'CustomBuild'
    sourcesdir = 'https://github.com/IO500/io500.git'

    @run_before('compile')
    def set_build_command(self):
        self.build_system.commands = ['./prepare.sh']

    @sanity_function
    def validate_build(self):
        return sn.assert_not_found('error', self.stderr)


# Base class for the IO500 Benchmark runs.
@rfm.simple_test
class IO500Benchmark(rfm.RunOnlyRegressionTest):
    '''Base IO500 benchmark class.'''

    descr = 'Run the IO500 benchmark.'
    valid_systems = ['archer2:compute']
    valid_prog_environs = ['PrgEnv-gnu']
    sourcesdir = 'src'
    keep_files = ['results'] # retain the results directory
    datadir = {'cwd':   './datafiles',
               'work1': '/mnt/lustre/a2fs-work1/work/z19/z19/shared',
               'work2': '/mnt/lustre/a2fs-work2/work/z19/z19/shared',
               'work3': '/mnt/lustre/a2fs-work3/work/z19/z19/shared',
               'work4': '/mnt/lustre/a2fs-work4/work/z19/z19/shared'}
    fs = parameter(['work4'])

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('IO500BuildTest', udeps.by_env)

    # Use the io500.sh script as our executable. Before using it, we need
    # to fix the preamble to correctly create and stripe the run directories.
    @require_deps
    def set_executable(self, IO500BuildTest):
        self.executable = './io500.sh'
        # Copy the full contents of the build directory to the test stage
        # directory. Then delete everything *before* the warning in io500.sh
        # and prepend what remains with the contents of io500-prologue.sh
        # which create the work directories and set their striping.
        self.prerun_cmds = ["cp -r " + IO500BuildTest().stagedir + "/* .",
                            "sed -i -n -E -e '/YOU SHOULD NOT EDIT/,$ p' " + self.executable,
                            "cat io500-prologue.sh " + self.executable + " > io500-fixed.sh",
                            "cp io500-fixed.sh " + self.executable]

    # Fix the path to the data directory in the .ini. The config is
    # only staged during the run phase, so we make it a task to complete
    # at the start of the job itself.
    @run_before('run')
    def fix_datadir(self):
        stagedir_name = os.path.split( self.stagedir )[-1]
        rundir = os.path.join(self.datadir[self.fs],stagedir_name)
        self.prerun_cmds.append("sed -i 's+./datafiles+" + rundir + "+' " + self.executable_opts[0])

    # Override the job launch. We don't want to run srun within the job script.
    # Instead just run io500.sh which will do the parallel launch internally.
    @run_after('setup')
    def set_launcher(self):
        self.job.launcher = getlauncher('local')()

    # If the job fails, there may be a huge data directory left. We will attempt to
    # clean this up manually and independently of the cleanup stage which follows the
    # performance stage (i.e. if the cleanup stage is not run).
    @run_after('performance')
    def data_cleanup(self):
        with osext.change_dir(self.stagedir):
            try:
                # Attempt to munlink datafiles. This should be more efficient than rm on Lustre.
                osext.run_command("find -P " + self.datadir[self.fs] + " -type f -print0 -o -type l -print0 | xargs -0 munlink")
            except:
                # If munlink failed, rm the entirety of datafiles the old-fashioned way.
                osext.run_command("rm -rf " + self.datadir[self.fs])
            else:
                # If munlink succeeded, delete the empty directories.
                osext.run_command("find -P " + self.datadir[self.fs] + " -type d -empty -delete")

    # Consider the test successful if 'Bandwidth' is found in output.
    @sanity_function
    def assert_io500(self):
        return sn.assert_found(r'Bandwidth', self.stdout)

    # Extract kIOPS performance for a single test.
    @performance_function('kIOPS')
    def extract_test_iops(self, kind='ior-easy-write'):
        return sn.extractsingle(r'\[RESULT\]\s+' + kind + r'\s+(\d+\.?\d*)\s+', self.stdout, 1, float)

    # Extract bandwidth performance for a single test.
    @performance_function('GiB/s')
    def extract_test_bw(self, kind='mdtest-easy-write'):
        return sn.extractsingle(r'\[RESULT\]\s+' + kind + r'\s+(\d+\.?\d*)\s+', self.stdout, 1, float)

    # Extract the final bandwidth score
    @performance_function('GiB/s')
    def extract_score_bw(self):
        return sn.extractsingle(r'\[SCORE\s\]\s+Bandwidth\s+(\d+\.?\d*)\s+', self.stdout, 1, float)

    # Extract the final IOPS score
    @performance_function('kIOPS')
    def extract_score_iops(self):
        return sn.extractsingle(r'\[SCORE\s\].+IOPS\s+(\d+\.?\d*)\s+', self.stdout, 1, float)

    # Extract the overall IO500 score.
    @performance_function('')
    def extract_score_total(self):
        return sn.extractsingle(r'\[SCORE\s\].+TOTAL\s+(\d+\.?\d*)\s+', self.stdout, 1, float)

    # Set the performance metrics we want to recover.
    @run_before('performance')
    def set_perf_variables(self):
        self.perf_variables = {
            'ior-easy-write': self.extract_test_bw('ior-easy-write'),
            'mdtest-easy-write': self.extract_test_iops('mdtest-easy-write'),
            'ior-hard-write': self.extract_test_bw('ior-hard-write'),
            'mdtest-hard-write': self.extract_test_iops('mdtest-hard-write'),
            'ior-easy-read': self.extract_test_bw('ior-easy-read'),
            'mdtest-easy-stat': self.extract_test_iops('mdtest-easy-stat'),
            'ior-hard-read': self.extract_test_bw('ior-hard-read'),
            'mdtest-hard-stat': self.extract_test_iops('mdtest-hard-stat'),
            'mdtest-easy-delete': self.extract_test_iops('mdtest-easy-delete'),
            'mdtest-hard-read': self.extract_test_iops('mdtest-hard-read'),
            'mdtest-hard-delete': self.extract_test_iops('mdtest-hard-delete'),
            'BANDWIDTH': self.extract_score_bw(),
            'IOPS': self.extract_score_iops(),
            'TOTAL': self.extract_score_total()
        }

# Test a simple debug run with one task on one node.
# This should complete in a few minutes.
@rfm.simple_test
class IO500RunDebug(IO500Benchmark):
    '''Run a small, fast IO500 debug test.'''
    fs = parameter(['work4'])

    def __init__(self):
        super().__init__()
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.time_limit = '10m'
        self.executable_opts = ['config-debug-run.ini']
        self.tags = {'performance'}

# Test a large run that should be valid for submission to the IO500 list.
# If the file system is under heavy load, this may take up to ~10 hours.
@rfm.simple_test
class IO500RunValid(IO500Benchmark):
    '''Run a large scale IO500 test.'''
    fs = parameter(['work4'])

    def __init__(self):
        super().__init__()
        self.num_tasks = 80
        self.num_tasks_per_node = 8
        self.num_cpus_per_task = 16
        self.time_limit = '10h'
        self.executable_opts = ['config-valid.ini']
        self.tags = {'performance','largescale'}

# Test a small run that should still indicate file system performance
@rfm.simple_test
class IO500RunSmall(IO500Benchmark):
    '''Run a large scale IO500 test.'''
    fs = parameter(['work4'])

    def __init__(self):
        super().__init__()
        self.num_tasks = 80
        self.num_tasks_per_node = 8
        self.num_cpus_per_task = 16
        self.time_limit = '1h'
        self.executable_opts = ['config-small.ini']
        self.tags = {'performance'}

