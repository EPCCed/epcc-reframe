# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn

from reframe.core.runtime import runtime


@rfm.simple_test
class FileSystemMountCheckWork1(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure ARCHER2 work1 file system mounted'
        self.valid_prog_environs = ['PrgEnv-cray']
        self.valid_systems = ['archer2:login']
        self.executable = '[[ -d  /mnt/lustre/a2fs-work1/ ]] && echo "work1-test file system found." '
        #self.executable_opts = ['']
        self.maintainers = ['James Richings']
        self.tags = {'production', 'craype'}
        self.sanity_patterns = sn.assert_found(r'^work1-test', self.stdout)


@rfm.simple_test
class FileSystemMountCheckWork2(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure ARCHER2 work2 file system mounted'
        self.valid_prog_environs = ['PrgEnv-cray']
        self.valid_systems = ['archer2:login']
        self.executable = '[[ -d  /mnt/lustre/a2fs-work2/ ]] && echo "work2-test file system found." '
        # self.executable_opts = []
        self.maintainers = ['James Richings']
        self.tags = {'production', 'craype'}
        self.sanity_patterns = sn.assert_found(r'^work2-test', self.stdout)

@rfm.simple_test
class FileSystemMountCheckWork3(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure ARCHER2 work3 file system mounted'
        self.valid_prog_environs = ['PrgEnv-cray']
        self.valid_systems = ['archer2:login']
        self.executable = '[[ -d  /mnt/lustre/a2fs-work3/ ]] && echo "work3-test file system found." '
        # self.executable_opts = []
        self.maintainers = ['James Richings']
        self.tags = {'production', 'craype'}
        self.sanity_patterns = sn.assert_found(r'^work3-test', self.stdout)

@rfm.simple_test
class FileSystemMountCheckWork4(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure ARCHER2 work4 file system mounted'
        self.valid_prog_environs = ['PrgEnv-cray']
        self.valid_systems = ['archer2:login']
        self.executable = '[[ -d  /mnt/lustre/a2fs-work4/ ]] && echo "work4-test file system found." '
        # self.executable_opts = []
        self.maintainers = ['James Richings']
        self.tags = {'production', 'craype'}
        self.sanity_patterns = sn.assert_found(r'^work4-test', self.stdout)

@rfm.simple_test
class FileSystemMountCheckWorknvme(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Ensure ARCHER2 NVMe file system mounted'
        self.valid_prog_environs = ['PrgEnv-cray']
        self.valid_systems = ['archer2:login']
        self.executable = '[[ -d  /mnt/lustre/a2fs-nvme/ ]] && echo "nvme-test file system found." '
        # self.executable_opts = []
        self.maintainers = ['James Richings']
        self.tags = {'production', 'craype'}
        self.sanity_patterns = sn.assert_found(r'^nvme-test', self.stdout)
