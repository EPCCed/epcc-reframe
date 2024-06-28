#!/usr/bin/env python
"""Test of download and build of xthi from repository master"""

import os

import reframe
import reframe.utility.sanity as sn

#  import reframe.utility.udeps as depends

REPOURL = "https://github.com/ARCHER2-HPC/xthi.git"


class XthiDownload(reframe.RunOnlyRegressionTest):
    """Download our very own xthi code."""

    descr = "xthi git clone"
    valid_systems = ["archer2:login", "cirrus:login"]
    valid_prog_environs = [
        "PrgEnv-cray",
        "PrgEnv-gnu",
        "PrgEnv-aocc",
        "gnu",
        "intel",
    ]
    executable = "git"
    executable_opts = ["clone", REPOURL]

    @sanity_function
    def validate_download(self):
        """Checks that download completed"""
        return sn.assert_eq(self.job.exitcode, 0)

    #  @sanity_function
    #  def sanity_check_download(self):
    #      """Checks that files were downloaded"""
    #      return sanity.assert_true(os.path.exists("xthi"))


@reframe.simple_test
class XthiCompilationTest(reframe.CompileOnlyRegressionTest):
    """Compile xthi via make"""

    descr = "xthi compilation test"
    valid_systems = ["archer2:login", "cirrus:login"]
    valid_prog_environs = [
        "PrgEnv-cray",
        "PrgEnv-gnu",
        "PrgEnv-aocc",
        "gnu",
        "intel",
    ]
    build_system = "Make"
    build_system_max_concurrency = 1
    repo = fixture(XthiDownload, scope="environment")

    @run_before("compile")
    def prepare_run(self):
        """Prepare run"""
        self.sourcesdir = os.path.join(
            self.repo.stagedir,
            "xthi",
            "src",
        )

    #  @run_after("init")
    #  def download_source(self):
    #      """Download fresh copy of repo"""
    #      self.depends_on("XthiDownLoadTest", udeps.fully)

    #  @require_deps
    #  def locate_source(self, XthiDownLoadTest):
    #      """Find source dir"""
    #      prefix = XthiDownLoadTest(part="login").stagedir
    #      self.sourcesdir = os.path.join(prefix, "xthi", "src")

    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sn.assert_not_found("error", self.stderr)
