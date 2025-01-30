#!/usr/bin/env python3

"""Compile and set-up centralised module for Quantum Espresso (QE) ReFrame Tests"""

import os
import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test 
class QESourceBuild(rfm.CompileOnlyRegressionTest): 
    """Build QE from source, mimicking the ARCHER2 7.1 module"""
    def __init__(self): 
        self.valid_systems = ["archer2:compute"]
        self.valid_prog_environs = ["PrgEnv-gnu"]
        local = True

        self.build_system = "CMake"
        self.modules = ["cray-fftw", "cray-hdf5-parallel", "cmake"]
        self.prebuild_cmds = [
            'wget https://github.com/QEF/q-e/archive/refs/tags/qe-7.1.tar.gz', 
            'tar xzf qe-7.1.tar.gz', 
            'cp FindSCALAPACK.cmake q-e-qe-7.1/cmake',
            'cd q-e-qe-7.1' 
        ]

        self.build_system.config_opts = ["-DCMAKE_Fortran_COMPILER=ftn", "-DCMAKE_C_COMPILER=cc", "-DQE_ENABLE_SCALAPACK=ON", "-DQE_ENABLE_HDF5=ON", '-DCMAKE_Fortran_FLAGS="-O3 -g -fallow-argument-mismatch -fopenmp -ffpe-summary=none"']
        self.build_system.builddir = "build"
        self.build_system.max_concurrency = 8 
        self.sanity_patterns = sn.assert_not_found('ERROR', self.stderr)

