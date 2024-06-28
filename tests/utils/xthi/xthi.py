#!/usr/bin/env python

"""
Test of download and build of xthi from repository master
"""

import os

import reframe
from reframe.utility import sanity, udeps

REPOURL = "https://github.com/ARCHER2-HPC/xthi.git"


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

    @run_after("init")
    def download_source(self):
        """Download fresh copy of repo"""
        self.depends_on("xthiDownLoadTest", udeps.fully)

    @require_deps
    def locate_source(self):
        """Find source dir"""
        prefix = XthiDownLoadTest(part="login").stagedir
        self.sourcesdir = os.path.join(prefix, "xthi", "src")

    @run_before("compile")
    def set_make_options(self):
        """Setup make options"""
        build_system_max_concurrency = 1

    @sanity_function
    def sanity_check_build(self):
        """Ensure build completed without errors"""
        return sanity.assert_not_found("error", self.stderr)


@reframe.simple_test
class XthiDownLoadTest(reframe.RunOnlyRegressionTest):
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
    def sanity_check_download(self):
        """Checks that files were downloaded"""
        return sanity.assert_true(os.path.exists("xthi"))
