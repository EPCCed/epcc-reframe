"""Compile QE"""

import reframe as rfm
import reframe.utility.sanity as sn
from qe_base import QEBaseEnvironment


class QESourceBuild(rfm.CompileOnlyRegressionTest):
    """Build QE from source, mimicking the ARCHER2 module version"""

    build_system = "CMake"
    modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]
    local = True
    build_locally = True
    version = f"{QEBaseEnvironment.qe_version}"
    prebuild_cmds = [
        f"wget https://github.com/QEF/q-e/archive/refs/tags/qe-{version}.tar.gz",
        f"tar xzf qe-{version}.tar.gz",
        f"cp FindSCALAPACK.cmake q-e-qe-{version}/cmake",
        f"cd q-e-qe-{version}",
    ]

    @run_before("compile")
    def prepare_build(self):
        """Prepare the system to build"""

        self.build_system.max_concurrency = 8
        self.build_system.builddir = "build"
        self.build_system.config_opts = [
            "-DCMAKE_Fortran_COMPILER=ftn",
            "-DCMAKE_C_COMPILER=cc",
            "-DQE_ENABLE_SCALAPACK=ON",
            "-DQE_ENABLE_HDF5=ON",
            '-DCMAKE_Fortran_FLAGS="-O3 -g \
                -fallow-argument-mismatch -fopenmp -ffpe-summary=none"',
        ]

    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("ERROR", self.stderr)
