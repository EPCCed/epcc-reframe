"""Base class for OpenFoam.org tests"""

import reframe as rfm


class OpenFOAMBase(rfm.RunOnlyRegressionTest):
    """ReFrame OpenFOAM test base class"""

    valid_prog_environs = ["PrgEnv-gnu"]

    maintainers = ["e.broadway@epcc.ed.ac.uk", "j.richings@epcc.ed.ac.uk"]
    use_multithreading = False
    tags = {"applications", "performance"}

    @run_after("init")
    def set_version_vars(self):
        """sets up version variables"""

        if self.current_system.name in ["archer2"]:
            self.v_major = "10"
            self.v_patch = "20230119"
        else:
            if self.current_system.name in ["cirrus-ex"]:
                self.v_major = "12"
                self.v_patch = "0"
            else:
                raise ValueError(f"OpenFoam version for System {self.current_system.name} not recognised .")

        self.version = f"{self.v_major}.{self.v_patch}"
