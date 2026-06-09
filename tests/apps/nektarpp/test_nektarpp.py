#!/usr/bin/env python3

"""Reframe test for Nektarplusplus"""

# Based on original work from:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn

NEKTAR_VERSION = "5.5.0"
NEKTAR_LABEL = "nektar"
NEKTAR_ARCHIVE = f"{NEKTAR_LABEL}-v{NEKTAR_VERSION}.tar.gz"
NEKTAR_NAME = f"{NEKTAR_LABEL}-{NEKTAR_VERSION}"


class FetchNektarplusplus(rfm.RunOnlyRegressionTest):
    """Test access to nektarplusplus source code"""

    descr = "Fetch Nektarplusplus"
    version = variable(str, value=NEKTAR_VERSION)
    executable = "wget"
    executable_opts = [f"https://gitlab.nektar.info/nektar/nektar/-/archive/v{NEKTAR_VERSION}/{NEKTAR_ARCHIVE}"]
    local = True
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"fetch"}

    @sanity_function
    def validate_download(self):
        """Validate download of source code sucessful"""
        return sn.assert_eq(self.job.exitcode, 0)


class CompileNektarplusplus(rfm.CompileOnlyRegressionTest):
    """Test compilation of nektarplusplus"""

    descr = "Build Nektarplusplus"
    build_system = "Make"
    fetch_nektarpp = fixture(FetchNektarplusplus, scope="environment")

    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"compile"}

    env_vars = {"CRAY_ADD_RPATH": "yes"}

    build_prefix = ""

    @run_before("compile")
    def prepare_build(self):
        """Prepare environment for build"""
        tarball = f"{NEKTAR_ARCHIVE}"
        self.build_prefix = f"{NEKTAR_NAME}"

        fullpath = os.path.join(self.fetch_nektarpp.stagedir, tarball)

        self.prebuild_cmds = [
            f"cp {fullpath} {self.stagedir}",
            f"tar xzf {tarball}",
            f"mv {NEKTAR_LABEL}-v{NEKTAR_VERSION} {self.build_prefix}",
            f"cd {self.build_prefix}",
            f"source ../cmake_nektarpp.sh {NEKTAR_LABEL}",
        ]
        self.build_system.max_concurrency = 8
        self.build_system.options = ["install"]

    @sanity_function
    def validate_compile(self):
        """Validate compilation by checking existance of binary"""
        return sn.path_isfile(f"{NEKTAR_NAME}/build/nektar/bin/IncNavierStokesSolver")


class TestNektarplusplusBase(rfm.RunOnlyRegressionTest):
    """Nektarplusplus Test"""

    descr = "Test Nektarplusplus"

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"performance", "applications"}

    compile_nektarpp = fixture(CompileNektarplusplus, scope="environment")

    modules = []

    env_vars = {"CRAY_ADD_RPATH": "yes"}

    keep_files = ["rfm_job.out"]

    @run_before("run")
    def prepare_run(self):
        """set up job execution"""

        self.executable = os.path.join(
            self.compile_nektarpp.stagedir,
            self.compile_nektarpp.build_prefix,
            "build",
            "nektar",
            "bin/IncNavierStokesSolver",
        )

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found(
            r"Total\s+Computation\s+Time\s+=\s+",
            self.keep_files[0],
            msg="Test_Nektarplusplus: Completion message not found",
        )

    @performance_function("seconds", perf_key="Computationtime")
    def extract_perf(self):
        """Extract performance value to compare with reference value"""
        return sn.extractsingle(
            r"Total\s+Computation\s+Time\s+=\s+(?P<Comptime>[0-9]+.[0-9]+)s",
            self.keep_files[0],
            "Comptime",
            float,
        )


@rfm.simple_test
class TestNektarpluslusSerial(TestNektarplusplusBase):
    """Nektarplusplus Test Serial"""

    descr = "Test Nektarplusplus Serial"

    num_nodes = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    num_tasks = num_nodes * num_tasks_per_node

    time_limit = "20m"

    executable_opts = ["TGV64_mesh.xml TGV64_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (953, -0.1, 0.1, "seconds")}}


@rfm.simple_test
class TestNektarpluslusParallel(TestNektarplusplusBase):
    """Nektarplusplus Test Parallel"""

    descr = "Test Nektarplusplus Parallel"

    num_nodes = 1
    num_tasks_per_node = 32
    num_cpus_per_task = 4
    num_tasks = num_nodes * num_tasks_per_node

    time_limit = "1h"

    executable_opts = ["TGV128_mesh.xml TGV128_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (1570, -0.1, 0.1, "seconds")}}


@rfm.simple_test
class TestNektarpluslusMultiNode(TestNektarplusplusBase):
    """Nektarplusplus Test Multi Node"""

    descr = "Test Nektarplusplus Multi Node"

    num_nodes = 4
    num_tasks_per_node = 8
    num_cpus_per_task = 16
    num_tasks = num_nodes * num_tasks_per_node

    time_limit = "1h"

    executable_opts = ["TGV128_mesh.xml TGV128_conditions.xml"]

    reference = {"archer2:compute": {"Computationtime": (1570, -0.1, 0.1, "seconds")}}
