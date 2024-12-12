"""ReFrame base module for Quantum Espresso (QE) tests"""

import reframe as rfm
import reframe.utility.sanity as sn

class QEBase(rfm.RunOnlyRegressionTest):
    """ReFrame base class for QE tests"""

    tags = {"applications", "performance"}
    valid_prog_environs = ["PrgEnv-gnu", "intel", "gcc"]
    extra_resources = {"qos": {"qos": "standard"}}

    executable = "pw.x"

    maintainers = ["e.broadway@epcc.ed.ac.uk"]
    strict_check = True 
 
    @sanity_function
    def assert_finished(self):
        # Using standard output
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("JOB DONE.", self.stdout)

    ### Need to add some performance_functions here... 