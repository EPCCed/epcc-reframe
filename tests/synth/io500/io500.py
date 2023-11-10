import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from reframe.core.backends import getlauncher
import os

# IO500 I/O benchmark - https://io500.org/

# TODO
# This won't run -- there's likely no clean way to get the benchmark
# test to run in the benchmark staging directory, while the executables
# live in the build staging directory, as io500.sh relies on $PWD in the
# 'YOU SHOULD NOT EDIT' portion.
# Path forward is to either combine the build and benchmark tests, so
# the run takes place automatically in the same staging directory, or
# to manipulate the benchmark test to use the same staging directory
# as the build test.

@rfm.simple_test
class IO500Benchmark(rfm.RunOnlyRegressionTest):
    '''Run the IO500 benchmark.'''

    def __init__(self):
        self.descr = 'Run the IO500 benchmark.'
        self.valid_systems = ['archer2:compute']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.sourcesdir = 'src'
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.time_limit = '10m'
        # For now just run the debug ini.
        self.config_file = "config-debug-run.ini"
        self.executable_opts = [self.config_file]

    @run_after('init')
    def set_dependencies(self):
        self.depends_on('IO500BuildTest', udeps.by_env)

    # Set the location of the io500.sh script and fix it for our use.
    # Ideally, I would like the ReFrame job to contain all of the fixed io500.sh
    # in place of the srun launch, but at the moment I can't see how to do that.
    @require_deps
    def set_executable(self, IO500BuildTest):
        stagedir = IO500BuildTest().stagedir
        # self.executable = os.path.join(stagedir, 'io500.sh')
        self.executable = './io500.sh'
        # Delete everything *before* the warning in io500.sh, then prepend
        # what remains with the contents of io500-prologue.sh which create
        # the work directories and set their striping.
        self.prerun_cmds = ["cp -r " + stagedir + "/* .",
                            "sed -i -n -E -e '/YOU SHOULD NOT EDIT/,$ p' " + self.executable,
                            "cat io500-prologue.sh " + self.executable + " > io500-fixed.sh",
                            "cp io500-fixed.sh " + self.executable]

    # Override the job launch. We don't want to run srun within the job script.
    # Instead just run io500.sh which will do the parallel launch internally.
    @run_after('setup')
    def set_launcher(self):
        self.job.launcher = getlauncher('local')()

    # Consider the test successful if 'Bandwidth' is found in output.
    @sanity_function
    def assert_io500(self):
        return sn.assert_found(r'Bandwidth', self.stdout)

@rfm.simple_test
class IO500BuildTest(rfm.CompileOnlyRegressionTest):
    '''Clone and build the IO500 source code.'''

    def __init__(self):
        self.descr = 'Clone and build the IO500 benchmark.'
        self.lang = ['c']
        self.valid_systems = ['archer2:compute']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.build_system = 'CustomBuild'
        self.sourcesdir = 'https://github.com/IO500/io500.git'
        self.build_system.commands = ['./prepare.sh']

    @sanity_function
    def validate_build(self):
        return sn.assert_not_found('error', self.stderr)
