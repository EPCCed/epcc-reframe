#!/usr/bin/env python3
"""ReFrame test for mdtest benchmark."""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import performance_function, run_before, sanity_function


class Mdtest(rfm.RunOnlyRegressionTest):
    """Run mdtest with the same configuration as test-run/mdtest/submit.sh."""

    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["mdtest-gcc"]

    num_cpus_per_task = 1
    time_limit = "20m"
    executable = "mdtest"

    env_vars = {
        "OMP_NUM_THREADS": "1",
        "OMP_PLACES": "cores",
    }

    tags = {"performance", "io"}

    # Set the number of tasks based on test parameters, defined in derived classes.
    @run_after("init")
    def set_num_tasks(self):
        """Set the number of tasks based on test parameters."""

        self.num_tasks = self.tasks_per_node * self.nodes
        self.num_tasks_per_node = self.tasks_per_node
        self.num_cpus_per_task = 288 // self.tasks_per_node

    @run_before("run")
    def set_executable_opts(self):
        """Set the executable options for mdtest based on test parameters."""

        opts = [
            "-F",
            "-C",
            "-T",
            "-r",
            "-n",
            str(self.num_files_per_task),
            "-N",
            str(self.num_tasks_per_node),
            "-d",
            self.work_directory,
        ]

        if self.multiple_directories:
            opts.append("-u")

        self.executable_opts = opts

    @run_before("run")
    def set_run_options(self):
        """Set srun options for the job launcher."""
        self.job.launcher.options = ["--mem=0", "--hint=nomultithread", "--distribution=block:block"]
        self.postrun_cmds = [f"rm -rf {self.work_directory}"]

    @sanity_function
    def assert_mdtest_finished(self):
        """Sanity checks."""
        return sn.assert_found(r"SUMMARY:\s+\(of\s+1\s+iterations\)", self.stdout)

    @performance_function("ops/s")
    def file_creation_mean(self):
        """Extract mean file creation rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*File creation\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def file_stat_mean(self):
        """Extract mean file stat rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*File stat\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def file_removal_mean(self):
        """Extract mean file removal rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*File removal\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def tree_creation_mean(self):
        """Extract mean tree creation rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*Tree creation\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )

    @performance_function("ops/s")
    def tree_removal_mean(self):
        """Extract mean tree removal rate from mdtest summary."""
        return sn.extractsingle(
            r"^\s*Tree removal\s*:\s*\S+\s+\S+\s+(\S+)",
            self.stdout,
            1,
            float,
            item=-1,
        )


@rfm.simple_test
class MdtestSingleNode(Mdtest):
    """Single node multiple directories mdtest test."""

    nodes = 1
    tasks_per_node = parameter([1, 8, 24, 96, 288])

    num_cpus_per_task = 1
    time_limit = "20m"
    num_files_per_task = 1000
    multiple_directories = True
    work_directory = parameter(["test_dir"])


@rfm.simple_test
class MdtestMultiNode(Mdtest):
    """Run mdtest multiple directories on multiple nodes."""

    nodes = parameter([2, 4, 8, 16])
    tasks_per_node = 288
    num_cpus_per_task = 1
    time_limit = "20m"
    num_files_per_task = 1000
    multiple_directories = True
    work_directory = parameter(["test_dir"])
