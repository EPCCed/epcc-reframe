"""ReFrame Tests for Quantum Espresso (QE)"""

import os

import reframe as rfm
from qe_base import QEBaseEnvironment
from qe_build import QESourceBuild


class QEAUSURF112ARCHER2(QEBaseEnvironment):
    """Base class to run the AUSURF112 QE Smoke test on ARCHER2"""

    num_tasks = 256
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    time_limit = "20m"
    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}
    n_nodes = 2
    extra_resources = {"qos": {"qos": "standard"}}
    modules = ["cray-fftw", "cray-hdf5-parallel"]
    executable_opts = ["-i ausurf.in"]

    if QEBaseEnvironment.qe_version == "7.1":
        reference = {"archer2:compute": {"PWSCF_wall": (260.0, -0.1, 0.1, "s")}}


@rfm.simple_test
class QEAUSURF112Module(QEAUSURF112ARCHER2):
    """Define the module and pw.x executable for QE on ARCHER2"""

    tags = {"applications", "performance"}
    executable = "pw.x"
    modules = [f"quantum_espresso/{QEBaseEnvironment.qe_version}"]


@rfm.simple_test
class QEAUSURF112SourceBuild(QEAUSURF112ARCHER2):
    """Define the modules and pw.x executable for QE on ARCHER2"""

    qe_binary = fixture(QESourceBuild, scope="environment")
    tags = {"applications", "performance", "compilation"}
    modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]

    @run_after("setup")
    def set_executable(self):
        """Sets up executable"""
        self.executable = os.path.join(
            self.qe_binary.stagedir, f"q-e-qe-{QEBaseEnvironment.qe_version}", "build/bin/pw.x"
        )
