import reframe.utility.sanity as sn
import reframe as rfm

# This test is designed to check if the programming environment is affected by
# the bug described at:
#  - https://stackoverflow.com/questions/63824065/lbound-of-an-array-changes-after-call-to-mpi-gatherv-when-using-mpi-f08-module
#  - https://gcc.gnu.org/pipermail/fortran/2020-September/055068.html
#
# This issue prevents the mpi_f08 interface being used. We expect GCC to potentially
# be affected and other compilers to not be affected.

@rfm.parameterized_test(['f90'])
class InterfaceBoundsTest(rfm.RegressionTest):
    def __init__(self, lang):
        self.valid_systems = ['archer2:login']
        self.valid_prog_environs = ['*']
        self.sourcepath = f'gcc-mpi_f08.{lang}'
        self.sanity_patterns = sn.assert_not_found(r'F', self.stdout)
        self.tags = {'compilers','basic','issues'}
        self.maintainers = ['a.turner@epcc.ed.ac.uk']

