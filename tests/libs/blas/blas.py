"""BLAS tests"""

import reframe as rfm
import reframe.utility.sanity as sn


class BLASBase(rfm.RegressionTest):
    """Base class for BLAS tests"""

    maintainers = ["e.broadway@epcc.ed.ac.uk"]
    build_system = "Make"
    executable_opts = ["3200", "150", "10000"]
    extra_resources = {"qos": {"qos": "standard"}}
    tags = {"performance", "functionality", "short"}

    @run_after("setup")
    def change_make_exe(self):
        """Rename files according to variant"""
        self.build_system.makefile = f"Makefile.{self.variant}"
        self.executable = f"./dgemv_{self.variant}.x"

    @sanity_function
    def assert_finished(self):
        """Checks that compilation finished"""
        return sn.assert_found(r"Normal", self.stdout)

    @performance_function("Gflops/s", perf_key="normal")
    def extract_normal(self):
        """Extract performance value of non-transposed dgemv run"""
        return sn.extractsingle(
            r"Normal\s+=\s+(?P<normal>\S+)", self.stdout, "normal", float
        )

    @performance_function("Gflops/s", perf_key="transpose")
    def extract_transpose(self):
        """Extract performance value of transposed dgemv run"""
        return sn.extractsingle(
            r"Transpose\s+=\s+(?P<transpose>\S+)",
            self.stdout,
            "transpose",
            float,
        )


@rfm.simple_test
class ARCHER2BlasTest(BLASBase):
    """ARCHER2 BLAS test class"""

    variant = parameter(["libsci", "mkl"])

    valid_systems = ["archer2"]
    valid_prog_environs = ["PrgEnv-gnu", "PrgEnv-aocc", "PrgEnv-cray"]
    env_vars = {"SLURM_CPU_FREQ_REQ": "2250000"}

    @run_after("setup")
    def load_module(self):
        """load correct module"""
        if self.variant == "mkl":
            self.modules = ["mkl"]
            self.prebuild_cmds = ["module load mkl"]
        else:
            self.prebuild_cmds = []

    @run_after("setup")
    def set_reference(self):
        """setup reference values"""
        if self.variant == "mkl":
            self.reference = {
                "archer2:compute": {
                    "normal": (14.00, -0.15, None, "Gflops/s"),
                    "transpose": (14.00, -0.15, None, "Gflops/s"),
                },
                "archer2:login": {
                    "normal": (14.00, -0.15, None, "Gflops/s"),
                    "transpose": (14.00, -0.15, None, "Gflops/s"),
                },
            }
        else:
            self.reference = {
                "archer2:compute": {
                    "normal": (16.75, -0.15, None, "Gflops/s"),
                    "transpose": (16.75, -0.15, None, "Gflops/s"),
                },
                "archer2:login": {
                    "normal": (16.75, -0.15, None, "Gflops/s"),
                    "transpose": (16.75, -0.15, None, "Gflops/s"),
                },
            }


@rfm.simple_test
class CirrusBlasTest(BLASBase):
    """Cirrus BLAS test class"""

    variant = parameter(["mkl"])

    valid_systems = ["cirrus"]
    valid_prog_environs = ["gnu", "intel"]
    reference = {
        "cirrus:compute": {
            "normal": (7.00, -0.15, None, "Gflops/s"),
            "transpose": (7.00, -0.15, None, "Gflops/s"),
        },
        "cirrus:login": {
            "normal": (7.00, -0.15, None, "Gflops/s"),
            "transpose": (7.00, -0.15, None, "Gflops/s"),
        },
    }

    @run_after("setup")
    def load_module(self):
        """load correct module"""
        if self.variant == "mkl":
            self.modules = ["intel-20.4/cmkl"]
            self.prebuild_cmds = ["module load intel-20.4/cmkl"]
        else:
            self.prebuild_cmds = []
