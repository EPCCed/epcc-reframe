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
    reference = {
        "archer2:compute" : {
            "PWSCF_wall": (260.0, -0.1, 0.1, "s")
        }
    }


@rfm.simple_test
class QEAUSURF112Module(QEAUSURF112ARCHER2):
    """Define the module and pw.x executable for QE on ARCHER2"""
    modules = ["quantum_espresso"]
    executable = "pw.x"


@rfm.simple_test
class QEAUSURF112SourceBuild(QEAUSURF112ARCHER2):
    """Define the modules and pw.x executable for QE on ARCHER2"""
    # depends_on("QESourceBuild")
    modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]
    qe_binary = fixture(QESourceBuild, scope="environment")

    # @require_deps
    # def set_executable(self, QESourceBuild):
    #     """ This sets the executable to the one built by reframe """
    #     self.executable = os.path.join(
    #         QESourceBuild().stagedir, 'q-e-qe-7.1', 'build', 'bin', 'pw.x'
    #     )

    @run_after("setup")
    def set_executable(self):
        """ Sets up executable"""
        self.executable = os.path.join(self. build_system.builddir, 'bin', 'pw.x')
