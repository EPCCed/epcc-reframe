# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class UlimitCheck(rfm.RegressionTest):
    def __init__(self):
        self.descr = 'Checking the output of ulimit -s in node.'
        self.valid_systems = ['archer2:compute','cirrus:compute']
        self.valid_prog_environs = ['PrgEnv-cray',  'PrgEnv-gnu',
                                    'PrgEnv-aocc','gnu','intel']
        self.sourcepath = 'ulimit.c'
        self.sanity_patterns = sn.all([
            sn.assert_found(r'The soft limit is unlimited', self.stdout),
            sn.assert_found(r'The hard limit is unlimited', self.stdout),
        ])

        self.ntasks = 1
        self.ntasks_per_node = 1
        self.time_limit = '1m'
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }

        self.tags = {'production', 'scs', 'craype'}
