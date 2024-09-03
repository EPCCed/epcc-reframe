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
class BenchioMediumTestMultiFile(rfm.RegressionTest):
    """BenchioMedium test class"""

    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    tags = {"performance", "io"}

    prerun_cmds = ["source create_striped_dirs.sh", "module remove darshan"]
    postrun_cmds = ["source delete_dirs.sh"]
    build_system = "CMake"
    modules = ["cray-hdf5-parallel"]

    @run_before("run")
    def setup_run(self):
        """Setup test directory"""
        stagedir_name = os.path.split(self.stagedir)[-1]
        self.env_vars["WRITE_DIR"] = os.path.join(self.write_dir_prefix, os.environ["USER"], stagedir_name)
        self.executable = self.stagedir + "/src/benchio"

    @run_before("compile")
    def set_compiler_flags(self):
        """Setup compiler flags"""
        self.build_system.config_opts = ["-DUSE_HDF5=TRUE"]

    @sanity_function
    def assert_benchio(self):
        """Sanity checks"""
        return sn.assert_found(r"Finished", self.stdout)

    @performance_function("GiB/s")
    def extract_write_bw(self):
        """Extract writing speed performance value"""
        return sn.extractsingle(
            r"Writing to unstriped/proc000000\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)",
            self.stdout,
            1,
            float,
        )

    @performance_function("s")
    def extract_write_time(self):
        """Extract writing time performance value"""
        return sn.extractsingle(
            r"Writing to unstriped/proc000000\.dat\W*\n\W*time\W*=\W*(\d+.\d*)\W*,\W*rate\W*=\W*\d+.\d*",
            self.stdout,
            1,
            float,
        )

    @run_before("performance")
    def set_perf_variables(self):
        """Sets reference values"""
        # Possibly redundant
        self.perf_variables = {
            "unstriped_file_bw": self.extract_write_bw(),
            "unstriped_file_time": self.extract_write_time(),
        }


@rfm.simple_test
class BenchioFPP16Nodes(BenchioMediumTestMultiFile):
    """Benchio 16 nodes test class"""

    write_dir_prefix = parameter(
        [
            "/mnt/lustre/a2fs-work1/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work2/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work3/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work4/work/z19/z19/shared",
            "/mnt/lustre/a2fs-nvme/work/z19/z19/shared",
        ]
    )

    num_nodes = 16
    num_tasks = 2048
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    time_limit = "20m"

    env_vars = {
        "OMP_NUM_THREADS": str(num_cpus_per_task),
    }

    executable_opts = ("2048 2048 2048 global proc unstriped fsync").split()

    tags = {"performance", "io"}


@rfm.simple_test
class BenchioFPP32Nodes(BenchioMediumTestMultiFile):
    """Benchio 16 nodes test class"""

    # could probably be parameterized with previous test

    write_dir_prefix = parameter(
        [
            "/mnt/lustre/a2fs-work1/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work2/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work3/work/z19/z19/shared",
            "/mnt/lustre/a2fs-work4/work/z19/z19/shared",
            "/mnt/lustre/a2fs-nvme/work/z19/z19/shared",
        ]
    )

    num_nodes = 32
    num_tasks = 2048
    num_tasks_per_node = 64
    num_cpus_per_task = 2
    time_limit = "1h"

    env_vars = {"OMP_NUM_THREADS": "1", "SRUN_CPUS_PER_TASK": "2"}

    executable_opts = ("8192 8192 8192 global proc unstriped fsync").split()

    tags = {"performance", "io"}
