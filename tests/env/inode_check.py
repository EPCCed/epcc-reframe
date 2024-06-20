# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.runtime import runtime

@rfm.simple_test
class inodeCheckARCHER2(rfm.RunOnlyRegressionTest):

    filesystem = parameter(
        [
        '/mnt/lustre/a2fs-work1',
        '/mnt/lustre/a2fs-work2',
        '/mnt/lustre/a2fs-work3',
        '/mnt/lustre/a2fs-work4',
        '/mnt/lustre/a2fs-nvme'
        ]
    )

    reference = {
        'archer2': {
            'MDT-0':  (75, None, 0.0, '% inodes'),
            'MDT-1':  (75, None, 0.0, '% inodes')
        }
    }

    descr = 'Check number of free inodes'
    valid_prog_environs = ['PrgEnv-cray']
    valid_systems = ['archer2:login']
    maintainers = ['Andy Turner']
    tags = {'production'}

    def __init__(self,**kwds):

        self.executable = 'lfs df -i'
        self.executable_opts = [self.filesystem]

    @sanity_function
    def validate_test(self):
        return sn.assert_found('MDT:0', self.stdout)

    @performance_function('% inodes', perf_key='MDT-0')
    def extract_MDT0(self):
        totinode = sn.extractsingle(r'\S+MDT0000\S+\s+(\S+)\s+.*', self.stdout, 1, int)
        usedinode = sn.extractsingle(r'\S+MDT0000\S+\s+\S+\s+(\S+)\s+.*', self.stdout, 1, int)
        return 100.0 * usedinode/totinode

    @performance_function('% inodes', perf_key='MDT-1')
    def extract_MDT1(self):
        totinode = sn.extractsingle(r'\S+MDT0001\S+\s+(\S+)\s+.*', self.stdout, 1, int)
        usedinode = sn.extractsingle(r'\S+MDT0001\S+\s+\S+\s+(\S+)\s+.*', self.stdout, 1, int)
        return 100.0 * usedinode/totinode

@rfm.simple_test
class inodeCheckCirrus(rfm.RunOnlyRegressionTest):

    filesystem = parameter(
        [
        '/mnt/lustre/e1000/'
        ]
    )

    reference = {
        'cirrus': {
            'MDT-0':  (75, None, 0.0, '% inodes'),
        }
    }

    descr = 'Check number of free inodes'
    valid_prog_environs = ['gnu']
    valid_systems = ['cirrus:login']
    maintainers = ['Andy Turner']
    tags = {'production'}

    def __init__(self,**kwds):

        self.executable = 'lfs df -i'
        self.executable_opts = [self.filesystem]

    @sanity_function
    def validate_test(self):
        return sn.assert_found('MDT:0', self.stdout)

    @performance_function('% inodes', perf_key='MDT-0')
    def extract_MDT0(self):
        totinode = sn.extractsingle(r'\S+MDT0000\S+\s+(\S+)\s+.*', self.stdout, 1, int)
        usedinode = sn.extractsingle(r'\S+MDT0000\S+\s+\S+\s+(\S+)\s+.*', self.stdout, 1, int)
        return 100.0 * usedinode/totinode

