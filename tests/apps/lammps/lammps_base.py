"""ReFrame base module for LAMMPS tests"""

import reframe as rfm
import reframe.utility.sanity as sn


class LAMMPSBase(rfm.RunOnlyRegressionTest):
    """ReFrame base class for LAMMPS tests"""

    valid_prog_environs = ["PrgEnv-gnu", "intel", "nvidia-mpi", "rocm-PrgEnv-cray"]
    executable = "lmp"
    extra_resources = {"qos": {"qos": "standard"}}

    keep_files = ["log.lammps"]

    maintainers = ["r.apostolo@epcc.ed.ac.uk"]
    strict_check = True
    tags = {"applications", "performance"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"Total wall time", self.keep_files[0])

    @performance_function("kJ/mol", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"\s+11000\s+\S+\s+\S+\s+(?P<energy>\S+)",
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
