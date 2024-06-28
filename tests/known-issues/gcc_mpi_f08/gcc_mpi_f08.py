#!/usr/bin/env python3

"""
Known issue mpi_f08 on gcc test

This test is designed to check if the programming environment is affected by the bug described at:
https://stackoverflow.com/questions/63824065/lbound-of-an-array-changes-after-call-to-mpi-gatherv-when-using-mpi-f08-module
https://gcc.gnu.org/pipermail/fortran/2020-September/055068.html

This issue prevents the mpi_f08 interface being used.
We expect GCC to potentially be affected and other compilers to not be affected.
"""

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class InterfaceBoundsTest(rfm.RegressionTest):
    """Test to check interface bounds -- gcc mpi_f08 known issue"""

    lang = parameter(["f90"])

    valid_systems = ["archer2:login", "cirrus:login"]
    valid_prog_environs = ["*"]
    tags = {"functionality", "short", "issues"}
    maintainers = ["a.turner@epcc.ed.ac.uk"]

    @run_after("init")
    def setup_path(self):
        """Sets up path"""
        self.sourcepath = f"gcc-mpi_f08.{self.lang}"

    @sanity_function
    def assert_notfound(self):
        """Checks that issue was not found"""
        return sn.assert_not_found(r"F", self.stdout)
