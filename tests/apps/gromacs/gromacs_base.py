import reframe as rfm
import reframe.utility.sanity as sn


class GromacsBaseCheck(rfm.RunOnlyRegressionTest):
    #  def __init__(self, output_file):
    #      super().__init__()
    #
    #      self.output_file = output_file
    #      self.valid_prog_environs = ["PrgEnv-gnu", "gnu", "nvidia-mpi"]
    #      self.executable = "gmx_mpi"
    #
    #      self.keep_files = [self.output_file]
    #
    #      self.maintainers = ["a.turner@epcc.ed.ac.uk"]
    #      self.strict_check = False
    #      self.use_multithreading = False
    #      self.extra_resources = {"qos": {"qos": "standard"}}
    #      self.tags = {"applications", "performance"}

    #  def __init__(self, output_file):
    #      super().__init__()
    #
    #      self.output_file = output_file

    valid_prog_environs = ["PrgEnv-gnu", "gnu", "nvidia-mpi"]
    executable = "gmx_mpi"

    keep_files = ["md.log"]

    maintainers = ["a.turner@epcc.ed.ac.uk"]
    strict_check = False
    use_multithreading = False
    extra_resources = {"qos": {"qos": "standard"}}
    tags = {"applications", "performance"}

    energy_reference = -12071400.0

    @sanity_function
    def assert_finished(self):
        return sn.assert_found(r"Finished mdrun", self.stdout)

    @performance_function(self)
    def assert_energy(self):
        return sn.extractsingle(
            r"\s+Potential\s+Kinetic En\.\s+Total Energy"
            r"\s+Conserved En\.\s+Temperature\n"
            r"(\s+\S+){2}\s+(?P<energy>\S+)(\s+\S+){2}\n"
            r"\s+Pressure \(bar\)\s+Constr\. rmsd",
            self.stdout,
            "energy",
            float,
            item=-1,
        )

    #  self.sanity_patterns = sn.all(
    #      [
    #          sn.assert_found("Finished mdrun", self.output_file),
    #          sn.assert_reference(energy, energy_reference, -0.01, 0.01),
    #      ]
    #  )

    @performance_function("ns/day", perf_key="perf")
    def extract_perf(self):
        return sn.extractsingle(
            r"Performance:\s+(?P<perf>\S+)",
            self.output_file,
            "perf",
            float,
        )
