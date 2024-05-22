"""ReFrame base module for VASP tests"""
import reframe as rfm
import reframe.utility.sanity as sn


class VASPBase(rfm.RunOnlyRegressionTest):
    """ReFrame base class for VASP tests"""

    valid_prog_environs = ["PrgEnv-gnu"]
    valid_systems = ["archer2:compute"]
#    executable = "lmp"

    keep_files = ["OUTCAR"]

    maintainers = ["a.turner@epcc.ed.ac.uk"]
    strict_check = True
    tags = {"applications", "performance", "nonstandard"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(r"Elapsed time (sec)", self.keep_files[0])

    @performance_function("eV", perf_key="energy")
    def extract_energy(self):
        """Extract value of system energy for performance check"""
        return sn.extractsingle(
            r"\s+free  energy   TOTEN\s+=\s+(?P<energy>\s+)",
            self.keep_files[0],
            "energy",
            float,
            item=-1,
        )

    @performance_function("LOOP+/hour", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        timing = sn.extractsingle(
            r"LOOP\+:\s+cpu time\s+\S+\s+real time\s+(?P<timing>\s+)",
            self.keep_files[0],
            "timing",
            float,
        )
        return 3600.0 / timing
