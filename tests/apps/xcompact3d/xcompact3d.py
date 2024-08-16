# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import os 
import re
import json

@rfm.simple_test
class xcompact3dLargeTest(rfm.RegressionTest):

    valid_systems = ['archer2:compute']
    valid_prog_environs = ['PrgEnv-gnu']

    tags = {'performance','largescale','applications'}

    def __init__(self,**kwds):

        super().__init__()
        self.num_nodes = 1024
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.num_tasks = self.num_nodes * self.num_tasks_per_node * self.num_cpus_per_task

        self.env_vars = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task)
        }

        self.modules = ["cmake/3.29.4"]

        self.time_limit = '1h'
        self.build_system = 'CMake'
        self.build_system.ftn="ftn"
        self.prebuild_cmds = ["git clone https://github.com/xcompact3d/Incompact3d.git", "cd Incompact3d"]
        self.builddir = "Incompact3d"
        self.executable = 'Incompact3d/bin/xcompact3d'
        self.executable_opts = ['large.i3d']

        self.sanity_patterns = sn.all([
            sn.assert_found('Good job', self.stdout)
        ])

        self.perf_patterns = {
            'steptime': sn.extractsingle(r'Averaged time per step \(s\):\s+(?P<steptime>\S+)',
                                     self.stdout, 'steptime', float)
        }
        

        self.reference = {
                'archer2:compute': {
                    'steptime': (6.3, -0.2, 0.2, 's')
                }
        }

        

