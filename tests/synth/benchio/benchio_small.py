#!/usr/bin/env python3
"""
Benchio Input/Output test

The test is parameterized on the folder where to write with parameter 'write_dir_prefix'.
You might want to choose a folder for each filesystem.
Currently test data is being written in the z19 shared directory on all 4 work filesystems
so this test must be run by a member of the z19 project on ARCHER2.

# Based on work by:
#   Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause
"""

import os

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class BenchioSmallTest(rfm.RegressionTest):
    """Benchio small test class"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"performance", "short", "io"}

    num_nodes = parameter([1, 2])

    write_dir_prefix = parameter(
        [
            "/mnt/lustre/a2fs-work1/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work2/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work3/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work4/work/z19/z19/shared",
            "/mnt/lustre/a2fs-nvme/work/z19/z19/shared",
        ]
    )

    executable_opts = ("1260 1260 1260 global mpiio hdf5 fsync").split()
    num_tasks = 128 * num_nodes
    num_tasks_per_node = 128
    num_cpus_per_task = 1

    env_vars = {"OMP_NUM_THREADS": str(num_cpus_per_task)}

    prerun_cmds = ["source create_striped_dirs.sh", "module remove darshan"]
    postrun_cmds = ["source delete_dirs.sh"]
    time_limit = "1h"
    build_system = "CMake"
    build_system.ftn = "ftn"
    modules = ["cray-hdf5-parallel"]

    @run_after("setup")
    def set_references_per_node(self):
        """set reference values"""
        if self.num_nodes == 1:
            self.reference = {
                "archer2:compute": {
                    "fullstriped_hdf5": (1.2, -0.4, 0.4, "GB/s"),
                    "unstriped_hdf5": (0.5, -0.3, 0.3, "GB/s"),
                    "fullstriped_mpiio": (1.2, -0.4, 0.4, "GB/s"),
                    "unstriped_mpiio": (0.6, -0.3, 0.3, "GB/s"),
                }
            }
        else:
            if self.num_nodes == 2:
                self.reference = {
                    "archer2:compute": {
                        "fullstriped_hdf5": (2.4, -0.4, 0.4, "GB/s"),
                        "unstriped_hdf5": (0.5, -0.5, 0.5, "GB/s"),
                        "fullstriped_mpiio": (2.0, -0.4, 0.4, "GB/s"),
                        "unstriped_mpiio": (0.5, -0.5, 0.5, "GB/s"),
                    }
                }
            else:
                raise ValueError("References are defined for calculations with 1 or 2 nodes")

    @performance_function("GiB/s")
    def extract_striped_hdf5(self):
        """Extract striped hdf5 rate"""
        return sn.extractsingle(
            r"Writing to fullstriped/hdf5\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)",
            self.stdout,
            1,
            float,
        )

    @performance_function("GiB/s")
    def extract_unstriped_hdf5(self):
        """Extract unstriped hdf5 rate"""
        return sn.extractsingle(
            r"Writing to unstriped/hdf5\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)",
            self.stdout,
            1,
            float,
        )

    @performance_function("GiB/s")
    def extract_unstriped_mpiio(self):
        """Extract unstriped mpiio rate"""
        return sn.extractsingle(
            r"Writing to unstriped/mpiio\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)",
            self.stdout,
            1,
            float,
        )

    @performance_function("GiB/s")
    def extract_striped_mpiio(self):
        """Extract striped mpiio rate"""
        return sn.extractsingle(
            r"Writing to fullstriped/mpiio\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)",
            self.stdout,
            1,
            float,
        )

    @run_before("run")
    def setup_run(self):
        """Setup test directory"""
        stagedir_name = os.path.split(self.stagedir)[-1]
        self.env_vars["WRITE_DIR"] = os.path.join(self.write_dir_prefix, stagedir_name)
        self.executable = self.stagedir + "/src/benchio"

    @run_before("compile")
    def set_compiler_flags(self):
        """Setup compiler flags"""
        self.build_system.config_opts = ["-DUSE_HDF5=TRUE"]

    @sanity_function
    def assert_benchio(self):
        """Sanity checks"""
        return sn.assert_found(r"Finished", self.stdout)
