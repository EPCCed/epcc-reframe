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

    prerun_cmds  = ['source create_striped_dirs.sh', 'module remove darshan']
    postrun_cmds  = ['source delete_dirs.sh']
    build_system = 'CMake'
    modules = [ "cray-hdf5-parallel", "craype-network-ucx", "cray-mpich-ucx" ]
        
    @run_before('run')
    def setup_run(self):
        stagedir_name=os.path.split( self.stagedir )[-1]
        self.env_vars["WRITE_DIR"]=os.path.join(self.write_dir_prefix,os.environ['USER'],stagedir_name)
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

    @performance_function('s')
    def extract_write_time(self, type='mpiio', striping='fullstriped'):
        return sn.extractsingle(r'Writing to ' + striping + '/' + type + r'\.dat\W*\n\W*time\W*=\W*(\d+.\d*)\W*,\W*rate\W*=\W*\d+.\d*',
                                self.stdout, 1, float)

    @run_before('performance')
    def set_perf_variables(self):
        self.perf_variables = {
            'fullstriped_mpiio_bw': self.extract_write_bw(type='mpiio', striping='fullstriped'),
            'fullstriped_mpiio_time': self.extract_write_time(type='mpiio', striping='fullstriped'),
            'fullstriped_hdf5_bw': self.extract_write_bw(type='hdf5', striping='fullstriped'),
            'fullstriped_hdf5_time': self.extract_write_time(type='hdf5', striping='fullstriped'),
        }

@rfm.simple_test
class BenchioMPIIOUCX16Nodes(benchioMPIIOUCXBase):

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
        self.time_limit = '1h'

        self.env_vars = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task)
        }

        self.executable_opts = ('2048 2048 2048 global mpiio hdf5 fullstriped fsync').split()
        
        self.tags = {'performance', 'io'}

@rfm.simple_test
class BenchioMPIIOUCXOpt16Nodes(benchioMPIIOUCXBase):

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
            "FI_OFI_RXM_SAR_LIMIT": "64K",
            "MPICH_MPIIO_HINTS": "*:cray_cb_write_lock_mode=2,*:cray_cb_nodes_multiplier=4"
        }

        self.executable_opts = ('2048 2048 2048 global mpiio hdf5 fullstriped fsync').split()
        
        self.tags = {'performance', 'io'}

@rfm.simple_test
class BenchioMPIIOUCXOpt16NodesAllstripe(benchioMPIIOUCXBase):

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
        self.time_limit = '1h'

        self.env_vars = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task),
            "FI_OFI_RXM_SAR_LIMIT": "64K",
            "MPICH_MPIIO_HINTS": "*:cray_cb_write_lock_mode=2,*:cray_cb_nodes_multiplier=4"
        }

        self.executable_opts = ('2048 2048 2048 global mpiio hdf5').split()
        
        self.tags = {'performance', 'io'}

@rfm.simple_test
class BenchioMPIIOUCX32Nodes(benchioMPIIOUCXBase):

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
        self.num_tasks = 4096
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = '1h'

        self.env_vars = {
            "OMP_NUM_THREADS": "1",
            "SRUN_CPUS_PER_TASK": "1"
        }

        self.executable_opts = ('4096 4096 4096 global mpiio hdf5 fullstriped fsync').split()
        
        self.tags = {'performance', 'io'}

@rfm.simple_test
class BenchioMPIIOUCXOpt32Nodes(benchioMPIIOUCXBase):

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
        self.num_tasks = 4096
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = '20m'

        self.env_vars = {
            "OMP_NUM_THREADS": "1",
            "SRUN_CPUS_PER_TASK": "1",
            "FI_OFI_RXM_SAR_LIMIT": "64K",
            "MPICH_MPIIO_HINTS": "*:cray_cb_write_lock_mode=2,*:cray_cb_nodes_multiplier=4"
        }

        self.executable_opts = ('4096 4096 4096 global mpiio hdf5 fullstriped fsync').split()
        
        self.tags = {'performance', 'io'}

