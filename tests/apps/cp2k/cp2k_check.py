#!/usr/bin/env python3

"""ReFrame tests for cp2k"""

import reframe as rfm
import reframe.utility.sanity as sn


class CP2KBaseCheck(rfm.RunOnlyRegressionTest):
    """ReFrame CP2K test base class"""

    # Which modules to load in test
    modules = ["cp2k"]
    # Identify the executable
    executable = "cp2k.psmp"
    # Additional Slurm parameters. Requires adding to config file first.
    extra_resources = {"qos": {"qos": "standard"}}

    maintainers = ["j.richings@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications"}


@rfm.simple_test
class CP2KARCHER2HFX(CP2KBaseCheck):
    """CP2K performance test"""

    # Select system to use
    valid_systems = ["archer2:compute"]
    # Output files to be retained
    keep_files = ["cp2k.out"]
    # Set Programming Environment
    valid_prog_environs = ["PrgEnv-gnu", "PrgEnv-gnu-hf"]
    # Description of test
    descr = "CP2K "
    # Command line options for executable
    executable_opts = ("-i input_bulk_HFX_3.inp -o cp2k.out ").split()
    # different cpu frequencies
    freq = ["2250000", "2000000"]
    # slurm parameters
    num_tasks = 384
    num_tasks_per_node = 16
    num_cpus_per_task = 8
    time_limit = "10m"
    # Reference value to validate run with
    energy_reference = -870.934788
    tags = CP2KBaseCheck.tags.union({"performance"})
    reference_performance = {
        "2000000": (350, -0.1, 0.1, "seconds"),
        "2250000": (250, -0.1, 0.1, "seconds"),
    }

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("CP2K   ", self.keep_files[0])

    @run_after("init")
    def setup_params(self):
        """sets up extra parameters"""
        # self.descr += self.freq
        if self.current_system.name in ["archer2"]:
            self.env_vars = {"OMP_NUM_THREADS": str(self.num_cpus_per_task), "OMP_PLACES": "cores"}

    @run_before("performance")
    def set_reference(self):
        """Changes reference values"""
        if self.current_system.name in ["archer2"]:
            # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
            self.reference["archer2:compute:performance"] = self.reference_performance[
                "2250000" if self.current_environ.name[-3:] == "-hf" else "2000000"
            ]

    reference = {"*": {"energy": (energy_reference, -0.01, 0.01, "a.u.")}}

    reference_performance = {
        "2000000": (350, -0.1, 0.1, "seconds"),
        "2250000": (250, -0.1, 0.1, "seconds"),
    }

    @performance_function("a.u.", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"ENERGY\| Total FORCE_EVAL \( QS \) energy \[a.u.\]:\s+(?P<energy>\S+)",
            self.keep_files[0],
            "energy",
            float,
        )

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"\s+CP2K(?:\s+\d+\.?\d*){5}\s+(?P<perf>\S+)",
            self.keep_files[0],
            "perf",
            float,
        )


@rfm.simple_test
class FetchCP2K(rfm.RunOnlyRegressionTest):
    """
    Fetch CP2K source code, which contains the regression tests and benchmarks.
    """

    descr = "Fetch cp2k code"
    version = variable(str, value="2025.2")
    executable = "wget"
    executable_opts = [f"https://github.com/cp2k/cp2k/archive/refs/tags/v{version}.tar.gz"]
    local = True
    valid_systems = ["cirrus-ex:login"]
    valid_prog_environs = ["PgEnv-gnu"]

    @sanity_function
    def validate_download(self):
        """Validate the download was successful"""
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class CP2KCPUCirrusExRegressionTests(CP2KBaseCheck):
    """
    CP2K regression tests for cirrus-ex

    This runs the CP2K tests from the CP2K regression test suite.
    They are good functionality tests but not very useful for performance.

    """

    # Select system to use
    valid_systems = ["cirrus-ex:compute"]
    # Set Programming Environment
    valid_prog_environs = ["PrgEnv-gnu"]
    # Description of test
    descr = "CP2K regression tests"
    launcher = "cp2k_reg_tests"

    # Command line options for executable

    executable = "cp2k.psmp"

    executable_opts = ["-v"]

    cp2k_src = fixture(FetchCP2K, scope="environment")

    env_vars = {"OMP_PLACES": "cores", "CP2K_APP": "$(which cp2k.psmp)", "CP2K_DIR": "${CP2K_APP::-10}"}

    @sanity_function
    def assert_all_tests_completed(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Status: OK", self.stdout)

    @run_before("run")
    def set_resources(self):
        """Sets up slurm parameters"""
        # slurm parameters
        self.num_tasks = self.current_partition.processor.num_cpus // 2
        self.num_tasks_per_node = self.current_partition.processor.num_cpus // 2
        self.num_cpus_per_task = 2
        self.time_limit = "20m"
        self.env_vars["OMP_NUM_THREADS"] = str(self.num_cpus_per_task)

    @run_before("run")
    def launch_reg_tests(self):
        """
        The command to launch the regression tests is a python script executed serially ( not in parallel).

        In this implementation we use pre-run commands.
        An alternative is to use a custom launcher.
        However this needs to be specified in the config,
        in a custom programming environment.
        I think that solution is worse , because it pollutes a configuration file with test specific logic.

        """

        source_tar_file = f"v{self.cp2k_src.version}.tar.gz"

        self.prerun_cmds = [
            f"cp {self.cp2k_src.stagedir}/{source_tar_file} .",
            f"tar -zxf {source_tar_file}",
            f'cp2k-{self.cp2k_src.version}/tests/do_regtest.py \
        --workbasedir=$(pwd) \
        --maxtasks=72 \
        --mpiranks=2 \
        --ompthreads=${{OMP_NUM_THREADS}} \
        --mpiexec="srun --ntasks=2 --cpus-per-task=${{OMP_NUM_THREADS}}" \
        $CP2K_DIR psmp',
        ]
