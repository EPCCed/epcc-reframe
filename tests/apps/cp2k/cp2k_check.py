#!/usr/bin/env python3

"""ReFrame test for cp2k"""

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
    # Output files to be retained
    keep_files = ["cp2k.out"]

    maintainers = ["j.richings@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications", "performance"}

    # Reference value to validate run with
    energy_reference = -870.934788

    reference = {
        "*": {"energy": (energy_reference, -0.01, 0.01, "a.u.")},
        "cirrus:compute": {"performance": (1300, -0.05, 0.05, "seconds")},
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
    # Set Programming Environment
    valid_prog_environs = ["PrgEnv-gnu"]
    # Description of test
    descr = "CP2K "
    # Command line options for executable
    executable_opts = ("-i input_bulk_HFX_3.inp -o cp2k.out ").split()
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


@rfm.simple_test
class CP2KCPUCirrus(CP2KBaseCheck):
    """CP2K test for Cirrus"""

    # Select system to use
    valid_systems = ["cirrus:compute"]
    # Set Programming Environment
    valid_prog_environs = ["gnu"]
    # Description of test
    descr = "CP2K test"
    # Command line options for executable
    executable_opts = ("-i input_bulk_HFX_3.inp -o cp2k.out ").split()
    # slurm parameters
    num_tasks = 360
    num_tasks_per_node = 18
    num_cpus_per_task = 2
    time_limit = "1h"

    env_vars = {
        "OMP_NUM_THREADS": str(num_cpus_per_task),
        "OMP_PLACES": "cores",
    }
