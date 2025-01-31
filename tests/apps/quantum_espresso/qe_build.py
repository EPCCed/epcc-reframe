"""Compile QE """

import os

import reframe as rfm
import reframe.utility.sanity as sn


class QESourceBuild(rfm.CompileOnlyRegressionTest):
    """Build QE from source, mimicking the ARCHER2 7.1 module"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    build_system = "CMake"
    modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]
    prebuild_cmds = [
        'wget https://github.com/QEF/q-e/archive/refs/tags/qe-7.1.tar.gz',
        'tar xzf qe-7.1.tar.gz',
        'cp FindSCALAPACK.cmake q-e-qe-7.1/cmake',
        'cd q-e-qe-7.1'
    ]

    build_system.config_opts = [
        "-DCMAKE_Fortran_COMPILER=ftn",
        "-DCMAKE_C_COMPILER=cc",
        "-DQE_ENABLE_SCALAPACK=ON",
        "-DQE_ENABLE_HDF5=ON",
        '-DCMAKE_Fortran_FLAGS="-O3 -g \
            -fallow-argument-mismatch -fopenmp -ffpe-summary=none"'
    ]
    build_system.builddir = "build"
    build_system.max_concurrency = 8
    # sanity_patterns = sn.assert_not_found('ERROR', stderr)

    @sanity_function
    def sanity_executable_exists(self):
        """Check that the executable was created"""
        build_dir = f"{self.builddir}/bin"
        return sn.path_exists(os.path.join(build_dir, "pw.x"))
