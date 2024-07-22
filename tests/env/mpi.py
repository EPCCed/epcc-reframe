#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class MpiInitTest(rfm.RegressionTest):
    """This test checks the value returned by calling MPI_Init_thread.

    Output should look the same for every prgenv
    (mpi_thread_multiple seems to be not supported):

    # 'single':
    ['mpi_thread_supported=MPI_THREAD_SINGLE
      mpi_thread_queried=MPI_THREAD_SINGLE 0'],

    # 'funneled':
    ['mpi_thread_supported=MPI_THREAD_FUNNELED
      mpi_thread_queried=MPI_THREAD_FUNNELED 1'],

    # 'serialized':
    ['mpi_thread_supported=MPI_THREAD_SERIALIZED
      mpi_thread_queried=MPI_THREAD_SERIALIZED 2'],

    # 'multiple':
    ['mpi_thread_supported=MPI_THREAD_SERIALIZED
      mpi_thread_queried=MPI_THREAD_SERIALIZED 2']
    """

    required_thread = parameter(["single", "funneled", "serialized", "multiple"])

    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc", "gnu", "intel"]
    build_system = "SingleSource"
    sourcepath = "mpi_init_thread.cpp"
    time_limit = "1m"
    extra_resources = {"qos": {"qos": "standard"}}
    tags = {"production", "craype"}
    cppflags = {
        "single": ["-D_MPI_THREAD_SINGLE"],
        "funneled": ["-D_MPI_THREAD_FUNNELED"],
        "serialized": ["-D_MPI_THREAD_SERIALIZED"],
        "multiple": ["-D_MPI_THREAD_MULTIPLE"],
    }

    mpithread_version = {
        "single": 0,
        "funneled": 1,
        "serialized": 2,
        "multiple": 3,
    }

    @run_after("init")
    def set_cpp_flags(self):
        """Sets up the cpp flags"""
        self.build_system.cppflags = self.cppflags[self.required_thread]

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        found_mpithread = sn.extractsingle(
            r"^mpi_thread_required=(\w+)\s+mpi_thread_supported=\w+\s+mpi_thread_queried=\w+\s+(\d)",
            self.stdout,
            1,
            int,
        )
        return sn.all(
            [
                sn.assert_found(r"tid=0 out of 1 from rank 0 out of 1", self.stdout),
                sn.assert_eq(found_mpithread, self.mpithread_version[self.required_thread]),
            ]
        )


@rfm.simple_test
class MpiHelloTest(rfm.RegressionTest):
    """MPI Hello World test"""

    valid_systems = ["archer2:compute", "cirrus:compute"]
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc", "gnu", "intel"]

    descr = "MPI Hello World"
    sourcepath = "mpi_helloworld.c"
    num_tasks_per_node = 1
    num_tasks = 2
    time_limit = "1m"
    extra_resources = {"qos": {"qos": "standard"}}
    tags = {"diagnostic", "ops", "craype"}

    @sanity_function
    def assert_finished(self):
        """Sanity checks"""
        num_processes = sn.extractsingle(
            r"Received correct messages from (?P<nprocs>\d+) processes", self.stdout, "nprocs", int
        )
        return sn.assert_eq(num_processes, self.num_tasks - 1)

    #  @property
    #  @deferrable
    #  def num_tasks_assigned(self):
    #      return self.job.num_tasks
