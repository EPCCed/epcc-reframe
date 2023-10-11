import reframe as rfm
import reframe.utility.sanity as sn


class GromacsBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ["PrgEnv-gnu", "gnu", "nvidia-mpi"]
        self.executable = "gmx_mpi"

        self.keep_files = [output_file]

        energy = sn.extractsingle(
            r"\s+Potential\s+Kinetic En\.\s+Total Energy"
            r"\s+Conserved En\.\s+Temperature\n"
            r"(\s+\S+){2}\s+(?P<energy>\S+)(\s+\S+){2}\n"
            r"\s+Pressure \(bar\)\s+Constr\. rmsd",
            output_file,
            "energy",
            float,
            item=-1,
        )
        energy_reference = -12071400.0

        self.sanity_patterns = sn.all(
            [
                sn.assert_found("Finished mdrun", output_file),
                sn.assert_reference(energy, energy_reference, -0.01, 0.01),
            ]
        )

        self.perf_patterns = {
            "perf": sn.extractsingle(
                r"Performance:\s+(?P<perf>\S+)", output_file, "perf", float
            )
        }

        self.maintainers = ["a.turner@epcc.ed.ac.uk"]
        self.strict_check = False
        self.use_multithreading = False
        self.extra_resources = {"qos": {"qos": "standard"}}
        self.tags = {"applications", "performance"}

