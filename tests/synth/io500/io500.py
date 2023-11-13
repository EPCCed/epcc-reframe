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

# Base class for the IO500 Benchmark runs.
@rfm.simple_test
class IO500Benchmark(rfm.RunOnlyRegressionTest):
    '''Base IO500 benchmark class.'''

    def __init__(self):
        self.descr = 'Run the IO500 benchmark.'
        self.valid_systems = ['archer2:compute']
        self.valid_prog_environs = ['PrgEnv-gnu']
        self.sourcesdir = 'src'
        self.keep_files = ['results'] # retain the results directory

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
                osext.run_command("find -P ./datafiles -type f -print0 -o -type l -print0 | xargs -0 munlink")
            except:
                # If munlink failed, rm the entirety of datafiles the old-fashioned way.
                osext.run_command("rm -rf ./datafiles")
            else:
                # If munlink succeeded, delete the empty directories.
                osext.run_command("find -P ./datafiles -type d -empty -delete")

    # Consider the test successful if 'Bandwidth' is found in output.
    @sanity_function
    def assert_io500(self):
        return sn.assert_found(r'Bandwidth', self.stdout)

# Test a simple debug run with one task on one node.
# This should complete in a few minutes.
@rfm.simple_test
class IO500RunDebug(IO500Benchmark):
    '''Run a small, fast IO500 debug test.'''
    def __init__(self):
        super().__init__()
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.time_limit = '10m'
        self.executable_opts = ['config-debug-run.ini']

# Test a large run that should be valid for submission to the IO500 list.
@rfm.simple_test
class IO500RunValid(IO500Benchmark):
    '''Run a large scale IO500 test.'''
    def __init__(self):
        super().__init__()
        self.num_tasks = 80
        self.num_tasks_per_node = 8
        self.time_limit = '10m'
        self.executable_opts = ['config-valid.ini']
