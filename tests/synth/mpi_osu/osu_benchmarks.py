#!/usr/bin/env python3
"""
MPI OSU benchmarks
# Based on work by:
#   Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause
"""

import os

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility import udeps


class OSUDownload(rfm.RunOnlyRegressionTest):
    """Download test"""

    descr = "OSU benchmarks download sources"
    valid_prog_environs = ["PrgEnv-gnu", "PrgEnv-cray", "PrgEnv-aocc", "gcc", "intel"]
    executable = "wget"
    executable_opts = ["http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-5.6.2.tar.gz"]
    local = True

    @sanity_function
    def validate_download(self):
        """Sanity Check"""
        return sn.assert_not_found("error", self.stderr)


class OSUBuild(rfm.CompileOnlyRegressionTest):
    """Build Test"""

    descr = "OSU benchmarks build test (currently fails with  Cray)"
    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["PrgEnv-gnu", "PrgEnv-cray", "PrgEnv-aocc", "gcc", "intel"]
    build_system = "Autotools"

    osu_benchmarks = fixture(OSUDownload, scope='session')

    @run_before("compile")
    def set_build_system_attrs(self):
        """setup concurrency"""
        tarball = "osu-micro-benchmarks-5.6.2.tar.gz" 
        self.build_prefix = tarball[:-7]
        fullpath = os.path.join(self.osu_benchmarks.stagedir, tarball)
        self.prebuild_cmds += [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 8

    @sanity_function
    def validate_build(self):
        """Sanity check"""
        return sn.assert_not_found("error", self.stderr)


class OSUBenchmarkTestBase(rfm.RunOnlyRegressionTest):
    """Base class of OSU benchmarks runtime tests"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["PrgEnv-gnu", "PrgEnv-cray", "PrgEnv-aocc", "gcc", "intel"]
    sourcesdir = None
    num_tasks = 2
    num_tasks_per_node = 1
    extra_resources = {"qos": {"qos": "standard"}}

    @sanity_function
    def validate_test(self):
        """Sanity checks"""
        return sn.assert_found(r"^8", self.stdout)


@rfm.simple_test
class OSULatencyTest(OSUBenchmarkTestBase):
    """Latency test"""

    descr = "OSU latency test"
    osu_binaries = fixture(OSUBuild, scope='environment')

    @require_deps
    def set_executable(self):
        """Set Executable"""
        self.executable = os.path.join(self.osu_binaries.stagedir,
                                       self.osu_binaries.build_prefix,
                                       "mpi", "pt2pt", "osu_latency")
        self.executable_opts = ["-x", "100", "-i", "1000"]

    @performance_function("us")
    def latency(self):
        """Extract performance value"""
        return sn.extractsingle(r"^8\s+(\S+)", self.stdout, 1, float)


@rfm.simple_test
class OSUBandwidthTest(OSUBenchmarkTestBase):
    """Bandwidth Test"""

    descr = "OSU bandwidth test"
    osu_binaries = fixture(OSUBuild, scope='environment')

    @require_deps
    def set_executable(self):
        """Set Executable"""
        self.executable = os.path.join(self.osu_binaries.stagedir,
                                     self.osu_binaries.build_prefix,
                                     "mpi", "pt2pt", "osu_bw")
        self.executable_opts = ["-x", "100", "-i", "1000"]

    @performance_function("MB/s")
    def bandwidth(self):
        """Extract performance value"""
        return sn.extractsingle(r"^4194304\s+(\S+)", self.stdout, 1, float)
 
 
@rfm.simple_test
class OSUAllreduceTest(OSUBenchmarkTestBase):
    """All reduce test"""


    descr = "OSU Allreduce test"
    mpi_tasks = parameter(1 << i for i in range(1, 5))
    osu_binaries = fixture(OSUBuild, scope='environment')

    @run_after("init")
    def set_num_tasks(self):
        """Sets number of tasks"""
        self.num_tasks = self.mpi_tasks

    @require_deps
    def set_executable(self):
        """Setup executable"""
        self.executable = os.path.join(self.osu_binaries.stagedir,
                                     self.osu_binaries.build_prefix,
                                     "mpi", "collective", "osu_allreduce")
        self.executable_opts = ["-m", "8", "-x", "1000", "-i", "20000"]

    @performance_function("us")
    def latency(self):
        """Extract performance value"""
        return sn.extractsingle(r"^8\s+(\S+)", self.stdout, 1, float)
