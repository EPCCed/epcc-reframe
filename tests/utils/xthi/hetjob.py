#!/usr/bin/env python

import os

import reframe as rfm
import reframe.utility.sanity as sanity
import reframe.utility.udeps as depends

"""
Test of SLURM hetjob using xthi as the executable (current module version)

Please do not be tempted to put the string 'hetjob' in any of the
test names, as this propagates to the job name directive, which
upsets SLURM.

These are really by way of smoke tests, as there's no attempt to
check the resulting placement at the moment.
"""

@rfm.simple_test
class SharedCommWorldTest(rfm.RunOnlyRegressionTest):

    """
    SLURM hetjob with 3 nodes (no OpenMP) as per frist example
    https://docs.archer2.ac.uk/user-guide/scheduler/#heterogeneous-jobs
    """
    def __init__(self):
        self.descr = "SLURM hetjob for xthi shared MPI_COM_WORLD"
        self.valid_systems = ["archer2:compute"]
        self.valid_prog_environs = ["*"]
        self.modules = ["xthi"]
        
        # Utter, utter kludge
        # 1 + 2 nodes; 8 + 2x4 MPI tasks
        self.hetgroup0 = "--het-group=0 --nodes=1 --ntasks=8 --ntasks-per-node=8 xthi"
        self.hetgroup1 = "--het-group=1 --nodes=2 --ntasks=8 --ntasks-per-node=4 xthi"
        self.executable = self.hetgroup0 + " : " + self.hetgroup1
        
        self.time_limit ="2m"
        # Kludge three nodes because we can't set the number of nodes explicitly
        self.num_tasks = 3
        self.num_tasks_per_node = 1
        self.env_vars = {"OMP_PLACES": "cores"}
        self.extra_resources = {'qos': {'qos': 'standard'}}

    @sanity_function
    def sanity_check_run(self):
     
        return sanity.assert_found("Node summary", self.stdout)


@rfm.simple_test
class SharedCommWorldWithOpenMPTest(rfm.RunOnlyRegressionTest):

    """
    SLURM hetjob with shared MPI_COMM_WORLD and OpenMP as per
    the mixed MPI/OpenMP example at
    https://docs.archer2.ac.uk/user-guide/scheduler/#heterogeneous-jobs
    """
    def __init__(self):
        self.descr = "SLURM hetjob for shared MPI_COM_WORLD with OpenMP"
        self.valid_systems = ["archer2:compute"]
        self.valid_prog_environs = ["*"]
        self.modules = ["xthi"]
        
        # Two nodes with 8 MPI tasks per node
        self.shared_args = " --nodes=1 --ntasks=8 --tasks-per-node=8 --cpus-per-task=16"
        self.openmp0     = " --export=all,OMP_NUM_THREADS=16"
        self.openmp1     = " --export=all,OMP_NUM_THREADS=1"
        self.hetgroup0   = "--het-group=0" + self.shared_args + self.openmp0 + " xthi"
        self.hetgroup1   = "--het-group=1" + self.shared_args + self.openmp1 + " xthi"
        self.executable  = self.hetgroup0 + " : " + self.hetgroup1
        
        self.time_limit ="2m"
        
        # Kludge two nodes because we can't set the number of nodes explicitly
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        
        self.env_vars = {"OMP_PLACES": "cores"}
        self.extra_resources = {'qos': {'qos': 'standard'}}

    @run_before("run")
    def unset_omp_num_threads(self):
        self.prerun_cmds = ["unset OMP_NUM_THREADS"]

    @sanity_function
    def sanity_check_run(self):

        return sanity.assert_found("Node summary", self.stdout)

