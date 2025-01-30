#!/usr/bin/env python3

"""ReFrame tests for Quantum Espresso (QE)"""

import os
import reframe as rfm
from qe_base import QEBaseEnvironment

class QEAUSURF112ARCHER2(QEBaseEnvironment):
    """Base class to run the AUSURF112 QE Smoke test on ARCHER2"""
    def __init__(self):
        self.num_tasks = 256
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = "20m"
        self.env_vars = {"OMP_NUM_THREADS": str(self.num_cpus_per_task)}
        self.n_nodes = 2
        self.extra_resources = {"qos": {"qos": "standard"}}
        self.modules = ["cray-fftw", "cray-hdf5-parallel"]
        self.executable_opts = ["-i ausurf.in"]
        self.reference = {
            "archer2:compute" : {
                "PWSCF_wall": (260.0, -0.1, 0.1, "s")
            }
        }

@rfm.simple_test
class QEAUSURF112Module(QEAUSURF112ARCHER2):
    """Define the module and pw.x executable for QE on ARCHER2""" 
    def __init__(self): 
        super().__init__()
        self.modules = ["quantum_espresso"]
        self.executable = "pw.x"


@rfm.simple_test
class QEAUSURF112SourceBuild(QEAUSURF112ARCHER2):
    """Define the modules and pw.x executable for QE on ARCHER2""" 
    def __init__(self):
        super().__init__()
        self.depends_on("QESourceBuild")
        self.modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]

    @require_deps
    def set_executable(self, QESourceBuild):
        """ This sets the executable to the one built by reframe """ 
        self.executable = os.path.join(
            QESourceBuild().stagedir, 'q-e-qe-7.1', 'build', 'bin', 'pw.x'
        )
