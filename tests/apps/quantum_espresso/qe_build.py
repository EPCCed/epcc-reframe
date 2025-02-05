"""Compile QE """

import os

import reframe as rfm
import reframe.utility.sanity as sn


class QESourceBuild(rfm.CompileOnlyRegressionTest):
    """Build QE from source, mimicking the ARCHER2 7.1 module"""

    build_system = "CMake"
    modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]
    local = True
    build_locally = True
    prebuild_cmds = [
            'wget https://github.com/QEF/q-e/archive/refs/tags/qe-7.1.tar.gz',
            'tar xzf qe-7.1.tar.gz',
            'cp FindSCALAPACK.cmake q-e-qe-7.1/cmake',
            'cd q-e-qe-7.1'
        ]

    @run_before("compile")
    def prepare_build(self):        
        self.build_system.max_concurrency = 8
        self.build_system.builddir = "build"
        self.build_system.config_opts = [
            "-DCMAKE_Fortran_COMPILER=ftn",
            "-DCMAKE_C_COMPILER=cc",
            "-DQE_ENABLE_SCALAPACK=ON",
            "-DQE_ENABLE_HDF5=ON",
            '-DCMAKE_Fortran_FLAGS="-O3 -g \
                -fallow-argument-mismatch -fopenmp -ffpe-summary=none"'
        ]

    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("ERROR", self.stderr)
