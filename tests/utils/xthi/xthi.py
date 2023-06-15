#!/usr/bin/env python

import os

import reframe
import reframe.utility.sanity as sanity
import reframe.utility.udeps as depends

"""
Test of download and build of xthi from repository master
"""

repoURL = "https://github.com/ARCHER2-HPC/xthi.git"

@reframe.simple_test
class xthiCompilationTest(reframe.CompileOnlyRegressionTest):

    """
    Compile xthi via make
    """

    descr = "xthi compilation test"
    valid_systems = ["archer2:login",'cirrus:login']
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc",'gnu','intel']
    build_system = "Make"

    @run_after("init")
    def download_source(self):

        self.depends_on("xthiDownLoadTest", depends.fully)

    @require_deps
    def locate_source(self, xthiDownLoadTest):

        prefix = xthiDownLoadTest(part="login").stagedir
        self.sourcesdir = os.path.join(prefix, "xthi", "src")

    @run_before("compile")
    def set_make_options(self):
        self.build_system_max_concurrency = 1

    @sanity_function
    def sanity_check_build(self):
        return sanity.assert_not_found("error", self.stderr)


@reframe.simple_test
class xthiDownLoadTest(reframe.RunOnlyRegressionTest):

    """
    Download our very own xthi code.
    """

    descr = "xthi git clone"
    valid_systems = ["archer2:login",'cirrus:login']
    valid_prog_environs = ["PrgEnv-cray", "PrgEnv-gnu", "PrgEnv-aocc",'gnu','intel']
    executable = "git"
    executable_opts = ["clone", repoURL]

    @sanity_function
    def sanity_check_download(self):

        return sanity.assert_true(os.path.exists("xthi"))


@reframe.simple_test
class xthiSmokeTest(reframe.RunOnlyRegressionTest):

    descr = "xthi compute test"
    valid_systems = ['cirrus:compute']
    valid_prog_environs = ['gnu','intel']
    executable = "xthi"
    executable_opts = ["clone", repoURL]

    @sanity_function
    def sanity_check_download(self):

        return sanity.assert_true(os.path.exists("xthi"))
