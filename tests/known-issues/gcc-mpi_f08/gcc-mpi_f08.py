import reframe.utility.sanity as sn
import reframe as rfm

# This test is designed to check if the programming environment is affected by
# the bug described at:
#  - https://stackoverflow.com/questions/63824065/lbound-of-an-array-changes-after-call-to-mpi-gatherv-when-using-mpi-f08-module
#  - https://gcc.gnu.org/pipermail/fortran/2020-September/055068.html
#
# This issue prevents the mpi_f08 interface being used. We expect GCC to potentially
# be affected and other compilers to not be affected.

@rfm.simple_test
class InterfaceBoundsTest(rfm.RegressionTest):

    lang = parameter(['f90'])

    def __init__(self):
        self.valid_systems = ['archer2:login','cirrus:login']
        self.valid_prog_environs = ['*']
        self.sourcepath = f'gcc-mpi_f08.{self.lang}'
        self.sanity_patterns = sn.assert_not_found(r'F', self.stdout)
        self.tags = {'functionality','short','issues'}
        self.maintainers = ['a.turner@epcc.ed.ac.uk']
