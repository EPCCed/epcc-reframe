#!/usr/bin/env python3

"""ReFrame test for cp2k"""

import reframe as rfm
import reframe.utility.sanity as sn


class CP2KBaseCheck(rfm.RunOnlyRegressionTest):
    """ReFrame CP2K test base class"""

    # self.cpufreq = rfm.core.builtins.parameter(['1500000','2000000','2250000'])

    # Set Programming Environment
    valid_prog_environs = ["PrgEnv-gnu"]
    # Which modules to load in test
    modules = ["cp2k"]
    # Identify the executable
    executable = "cp2k.psmp"
    # Command line options for executable
    executable_opts = ("-i input_bulk_HFX_3.inp -o cp2k.out ").split()
    # Additional Slurm parameters. Requires adding to config file first.
    extra_resources = {"qos": {"qos": "standard"}}
    # Output files to be retained
    keep_files = ["cp2k.out"]

    maintainers = ["j.richings@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications", "performance"}

    # Reference value to validate run with
    energy_reference = -870.934788

    reference = {
        "*": {"energy": (energy_reference, -0.01, 0.01, "a.u.")},
        #  "archer2:compute": {"energy": (energy_reference, -0.01, 0.01, "a.u.")},
    }

    reference_performance = {
        "2000000": (350, -0.1, 0.1, "seconds"),
        "2250000": (250, -0.1, 0.1, "seconds"),
    }

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("CP2K   ", self.keep_files[0])

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
class CP2KARCHER2(CP2KBaseCheck):
    """CP2K test"""

    # Select system to use
    valid_systems = ["archer2:compute"]
    # Description of test
    descr = "CP2K "
    # different cpu frequencies
    freq = parameter(["2250000", "2000000"])
    # slurm parameters
    num_tasks = 384
    num_tasks_per_node = 16
    num_cpus_per_task = 8
    time_limit = "10m"

    reference_performance = {
        "2000000": (350, -0.1, 0.1, "seconds"),
        "2250000": (250, -0.1, 0.1, "seconds"),
    }

    @run_after("init")
    def setup_params(self):
        """sets up extra parameters"""
        self.descr += self.freq
        if self.current_system.name in ["archer2"]:
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "OMP_PLACES": "cores",
                "SLURM_CPU_FREQ_REQ": self.freq,
            }

    @run_before("performance")
    def set_reference(self):
        """Changes reference values"""
        if self.current_system.name in ["archer2"]:
            # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
            self.reference[
                "archer2:compute:performance"
            ] = self.reference_performance[self.freq]


# Cirrus default CPUfreq
# @rfm.simple_test
# class CP2KCPUCheckCirrus(CP2KBaseCheck):
#     def __init__(self):
#         super().__init__('cp2k.out')
#
#         # Select system to use
#         self.valid_systems = ['cirrus:compute']
#
#         # Description of test
#         self.descr = 'CP2K check Cirrus'
#         # Command line options for executable
#         self.executable_opts = ('-i input_bulk_HFX_3.inp -o cp2k.out ').split()
#
#         if (self.current_system.name in ['cirrus']):
#            self.modules = ['cp2k']
#            self.num_tasks = 360
#            self.num_tasks_per_node = 18
#            self.num_cpus_per_task = 2
#            self.time_limit = '1h'
#            self.env_vars = {
#                 'OMP_NUM_THREADS': str(self.num_cpus_per_task),
#                 'OMP_PLACES': 'cores',
#                 }
#
#     @run_before('run')
#     def set_task_distribution(self):
#         self.job.options = ['--distribution=block:block']
