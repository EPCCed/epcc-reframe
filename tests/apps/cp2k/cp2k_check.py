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
        "cirrus:compute": {"energy": (energy_reference, -0.01, 0.01, "a.u.")},
        "archer2:compute": {"energy": (energy_reference, -0.01, 0.01, "a.u.")},
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

    #  @run_before("run")
    #  def set_task_distribution(self):
    #      """change distribution"""
    #      self.job.options = ["--distribution=block:block"]


@rfm.simple_test
class CP2KARCHER2(CP2KBaseCheck):
    """2.25 Ghz test"""

    # Select system to use
    valid_systems = ["archer2:compute"]
    # Description of test
    descr = "CP2K "
    # different cpu frequencies
    freq = parameter([("2250000", 250), ("2000000", 350)])
    # Default performance test reference value
    #  reference["archer2:compute"]["performance"] = (, -0.1, 0.1, "seconds")
    # slurm parameters
    num_tasks = 384
    num_tasks_per_node = 16
    num_cpus_per_task = 8
    time_limit = "10m"

    @run_after("init")
    def setup_params(self):
        """sets up extra parameters"""
        self.descr += self.freq[0]
        if self.current_system.name in ["archer2"]:
            reference["archer2:compute"]["performance"] = (self.freq[1], -0.1, 0.1, "seconds")
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "OMP_PLACES": "cores",
                "SLURM_CPU_FREQ_REQ": self.freq[0],
            }

    #  @run_before("run")
    #  def setup_perf(self):
    #      """Changes reference values"""
    #      if self.current_system.name in ["archer2"] and self.freq == "2250000":
    #          # Change performance test reference value
    #          self.reference["archer2:compute"]["performance"] = (250, -0.1, 0.1, "seconds")


#  @rfm.simple_test
#  class CP2KCPUCheck225GHz(CP2KBaseCheck):
#      """2.25 Ghz test"""
#
#      # Select system to use
#      valid_systems = ["archer2:compute"]
#      # Description of test
#      descr = "CP2K 2.25Ghz check"
#      # Performance test reference values
#      reference["archer2:compute"]["performance"] = (250, -0.1, 0.1, "seconds")
#
#      @run_after("init")
#      def setup_nnodes(self):
#          """sets up number of tasks per node"""
#          if self.current_system.name in ["archer2"]:
#              self.modules = ["cp2k"]
#              self.num_tasks = 384
#              self.num_tasks_per_node = 16
#              self.num_cpus_per_task = 8
#              self.time_limit = "1h"
#              self.env_vars = {
#                  "OMP_NUM_THREADS": str(self.num_cpus_per_task),
#                  "OMP_PLACES": "cores",
#                  "SLURM_CPU_FREQ_REQ": "2250000",
#              }
#
#
#  @rfm.simple_test
#  class CP2KCPUCheck2GHz(CP2KBaseCheck):
#      """2 Ghz test"""
#
#      # Select system to use
#      valid_systems = ["archer2:compute"]
#      # Description of test
#      descr = "CP2K check 2Ghz check"
#      # Command line options for executable
#      executable_opts = ("-i input_bulk_HFX_3.inp -o cp2k.out ").split()
#      # Performance test reference values
#      reference["archer2:compute"]["performance"] = (340, -0.1, 0.1, "seconds")
#
#      @run_after("init")
#      def setup_nnodes(self):
#          """sets up number of tasks per node"""
#          if self.current_system.name in ["archer2"]:
#              # Total number of tasks in slurm
#              self.num_tasks = 384
#              # Task per node in slurm
#              self.num_tasks_per_node = 16
#              # CPU's per task in slurm
#              self.num_cpus_per_task = 8
#              # Slurm job time limit
#              self.time_limit = "1h"
#              # Other Environment parameters to set
#              self.env_vars = {
#                  "OMP_NUM_THREADS": str(self.num_cpus_per_task),
#                  "OMP_PLACES": "cores",
#                  "SLURM_CPU_FREQ_REQ": "2000000",
#              }


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
