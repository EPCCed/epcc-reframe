# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import os 
import re
import json

'''
Benchio Input/Output test

The test is parameterized on the folder where to write with parameter 'write_dir_prefix'. You might want to choose a folder for each filesystem.
Currently test data is being written in the z19 shared directory on all 4 work filesystems so this test must be run by a member of the z19
project on ARCHER2.
'''

@rfm.simple_test
class benchioMPIIOUCXBase(rfm.RegressionTest):

    valid_systems = ['archer2:compute']
    valid_prog_environs = ['PrgEnv-gnu']

    tags = {'performance','io'}

    prerun_cmds  = ['source create_striped_dirs.sh']
    postrun_cmds  = ['source delete_dirs.sh']
    build_system = 'CMake'
    modules = [ "cray-hdf5-parallel" ]
        
    @run_before('run')
    def setup_run(self):
        stagedir_name=os.path.split( self.stagedir )[-1]
        self.env_vars["WRITE_DIR"]=os.path.join(self.write_dir_prefix,stagedir_name)
        self.executable= self.stagedir + "/src/benchio"

    @run_before('compile')
    def set_compiler_flags(self):

        self.build_system.config_opts= ["-DUSE_HDF5=TRUE" ]
    
    @sanity_function
    def assert_benchio(self):
        return sn.assert_found(r'Finished', self.stdout)

    @performance_function('GiB/s')
    def extract_write_bw(self, type='mpiio', striping='fullstriped'):
        return sn.extractsingle(r'Writing to ' + striping + '/' + type + r'\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)',
                                self.stdout, 1, float)

    @run_before('performance')
    def set_perf_variables(self):
        self.perf_variables = {
            'fullstriped_mpiio': self.extract_write_bw(type='mpiio', striping='fullstriped'),
            'fullstriped_hdf5': self.extract_write_bw(type='hdf5', striping='fullstriped')
        }

@rfm.simple_test
class BenchioMPIIO16Nodes(benchioMPIIOUCXBase):

    write_dir_prefix = parameter(
        [
        '/mnt/lustre/a2fs-work1/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work2/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work3/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work4/work/z19/z19/shared',
        '/mnt/lustre/a2fs-nvme/work/z19/z19/shared'
        ]
    )

    def __init__(self):
        super().__init__()

        self.num_nodes = 16
        self.num_tasks = 2048
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = '20m'

        self.env_vars = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task),
        }

        self.executable_opts = ('2048 2048 2048 global mpiio hdf5 fullstriped').split()
        
        self.tags = {'performance', 'io'}


@rfm.simple_test
class BenchioMPIIO32Nodes(benchioMPIIOUCXBase):

    write_dir_prefix = parameter(
        [
        '/mnt/lustre/a2fs-work1/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work2/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work3/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work4/work/z19/z19/shared',
        '/mnt/lustre/a2fs-nvme/work/z19/z19/shared'
        ]
    )

    def __init__(self):
        super().__init__()

        self.num_nodes = 32
        self.num_tasks = 2048
        self.num_tasks_per_node = 64
        self.num_cpus_per_task = 2
        self.time_limit = '2h'

        self.env_vars = {
            "OMP_NUM_THREADS": "1",
            "SRUN_CPUS_PER_TASK": "2"
        }

        self.executable_opts = ('8192 8192 8192 global mpiio hdf5 fullstriped').split()
        
        self.tags = {'performance', 'io'}

