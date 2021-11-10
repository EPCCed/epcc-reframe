# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class MpiTCheck(rfm.RegressionTest):
    def __init__(self):
        self.descr = 'Checks MPI_T control/categories'
        self.valid_systems = ['archer2:compute']
        self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu', 'PrgEnv-aocc']
        self.build_system = 'SingleSource'
        self.sourcepath = 'mpit_vars.c'
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.time_limit = "1m"
        self.variables = {'MPITEST_VERBOSE': '1', 'MPICH_VERSION_DISPLAY': '1'}
        self.rpt = 'rpt'
        self.executable_opts = [f'&> {self.rpt}']
        self.tags = {'production', 'craype', 'maintenance'}

    @rfm.run_before('sanity')
    def set_sanity(self):
        # 1/ MPI Control Variables:
        # --- extract reference data:
        regex = r'^(?P<vars>MPIR\S+)$'
        ref = os.path.join(self.stagedir, 'mpit_control_vars.ref')
        self.ref_control_vars = sorted(sn.extractall(regex, ref, 'vars'))
        # --- extract runtime data:
        regex = r'^\t(?P<vars>MPIR\S+)\t'
        rpt = os.path.join(self.stagedir, self.rpt)
        self.run_control_vars = sorted(sn.extractall(regex, rpt, 'vars'))
        # 2/ MPI Category:
        # --- extract reference data:
        regex = r'^(?P<category>.*)$'
        ref = os.path.join(self.stagedir, 'mpit_categories.ref')
        ref_cat_vars = sorted(sn.extractall(regex, ref, 'category'))
        self.ref_cat_vars = list(filter(None, ref_cat_vars))
        # --- extract runtime data:
        regex = (r'^(?P<category>Category \w+ has \d+ control variables, \d+'
                 r' performance variables, \d+ subcategories)')
        rpt = os.path.join(self.stagedir, self.rpt)
        self.run_cat_vars = sorted(sn.extractall(regex, rpt, 'category'))
        # 3/ Extracted lists can be compared (when sorted):
        self.sanity_patterns = sn.all([
            sn.assert_eq(self.ref_control_vars, self.run_control_vars),
            sn.assert_eq(self.ref_cat_vars, self.run_cat_vars),
        ])
