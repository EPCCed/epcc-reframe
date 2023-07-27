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
class benchioMediumTest(rfm.RegressionTest):

    valid_systems = ['archer2:compute']
    valid_prog_environs = ['PrgEnv-gnu']

    tags = {'performance','short','io'}

    num_nodes = parameter( [16] )

    write_dir_prefix = parameter(
        [
        '/mnt/lustre/a2fs-work1/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work2/work/z19/z19/shared',
        '/mnt/lustre/a2fs-work3/work/z19/z19/shared',
        '/mnt/lustre/a2fs-nvme/work/z19/z19/shared'
        ]
    )

    def set_references_per_node(self):

        if self.num_nodes == 16:
            self.reference = {
                'archer2:compute': {
                'fullstriped_hdf5': ( 10.0, -0.5, 0.5 ,'GB/s'),
                'unstriped_hdf5': ( 1.2, -0.8, 0.8 ,'GB/s'),
                'fullstriped_mpiio': ( 10.0, -0.5, 0.5 ,'GB/s'),
                'unstriped_mpiio': ( 1.2, -0.8, 0.8 ,'GB/s')
                }
            }
        else:
            raise Exception("References are defined for calculations with 16 nodes")


    def __init__(self,**kwds):

        super().__init__()
        self.executable_opts = ('2048 2048 2048 global mpiio hdf5').split()
        self.num_tasks = 128 * self.num_nodes
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1

        self.env_vars = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task),
            "FI_OFI_RXM_SAR_LIMIT": "64K",
            "MPICH_MPIIO_HINTS": "*:cray_cb_write_lock_mode=2,*:cray_cb_nodes_multiplier=4"
        }

        self.prerun_cmds  = ['source create_striped_dirs.sh']
        self.postrun_cmds  = ['source delete_dirs.sh']
        self.time_limit = '20m'
        self.build_system = 'CMake'
        self.build_system.ftn="ftn"
        self.modules = [  "cray-hdf5-parallel", "craype-network-ucx", "cray-mpich-ucx" ]
        

        self.perf_patterns = {
            'fullstriped_hdf5': sn.extractsingle(r'Writing to fullstriped/hdf5\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)',
                                     self.stdout, 1, float),
            'unstriped_hdf5': sn.extractsingle(r'Writing to unstriped/hdf5\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)',
                                     self.stdout, 1, float),
            'unstriped_mpiio': sn.extractsingle(r'Writing to unstriped/mpiio\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)',
                                    self.stdout, 1, float),
            'fullstriped_mpiio': sn.extractsingle(r'Writing to fullstriped/mpiio\.dat\W*\n\W*time\W*=\W*\d+.\d*\W*,\W*rate\W*=\W*(\d+.\d*)',
                                    self.stdout, 1, float)
        }

        self.set_references_per_node()

        
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