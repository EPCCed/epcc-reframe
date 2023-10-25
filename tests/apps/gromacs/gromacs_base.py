"""ReFrame base module for GROMACS tests"""
import reframe as rfm
import reframe.utility.sanity as sn


class GromacsBaseCheck(rfm.RunOnlyRegressionTest):
    """ReFrame base class for GROMACS tests"""

    valid_prog_environs = ["PrgEnv-gnu", "gnu", "nvidia-mpi"]
    executable = "gmx_mpi"

    keep_files = ["md.log"]

    maintainers = ["a.turner@epcc.ed.ac.uk"]
    strict_check = True
    tags = {"applications", "performance"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"Finished mdrun", self.keep_files[0])

    @performance_function("kJ/mol", perf_key="energy")
    def extract_energy(self):
        """Extracts value of system energy for performance check"""
        return sn.extractsingle(
            r"\s+Potential\s+Kinetic En\.\s+Total Energy"
            r"\s+Conserved En\.\s+Temperature\n"
            r"(\s+\S+){2}\s+(?P<energy>\S+)(\s+\S+){2}\n"
            r"\s+Pressure \(bar\)\s+Constr\. rmsd",
            self.keep_files[0],
            "energy",
            float,
            item=-1,
        )

    @performance_function("ns/day", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"Performance:\s+(?P<perf>\S+)",
            self.keep_files[0],
            "perf",
            float,
        )
