"""Base class for OpenFoam.org tests"""

import reframe as rfm
import reframe.utility.sanity as sn


class OpenFOAMBase(rfm.RunOnlyRegressionTest):
    """ReFrame OpenFOAM test base class"""
    
 
    valid_prog_environs = ["PrgEnv-gnu"]
    
    maintainers = ["e.broadway@epcc.ed.ac.uk", "j.richings@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications", "performance"}

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("End", self.stdout)

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"ExecutionTime\s+=\s+(?P<time>\d+.?\d*\s+)s\s+ClockTime\s+=\s+\d*\s+s\n\nEnd",
            self.stdout,
            "time",
            float,
        )
    @run_after("init")
    def set_version_vars(self):
        """sets up version variables"""

        if self.current_system.name in ["archer2"]:
            self.v_major = "10"
            self.v_patch = "20230119" 
        if self.current_system.name in ["cirrus-ex"]:
            self.v_major = "12"
            self.v_patch = "0"
        else:
            raise ValueError(f"OpenFoam version for System {self.current_system.name} not recognised .")
        self.version = f"{self.v_major}-{self.v_patch}"
        

 

