#!/usr/bin/env python

"""
Test of SLURM hetjob using xthi as the executable (current module version)

Please do not be tempted to put the string 'hetjob' in any of the
test names, as this propagates to the job name directive, which
upsets SLURM.

These are really by way of smoke tests, as there's no attempt to
check the resulting placement at the moment.
"""

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SharedCommWorldTest(rfm.RunOnlyRegressionTest):

    """
    SLURM hetjob with 3 nodes (no OpenMP) as per first example
    https://docs.archer2.ac.uk/user-guide/scheduler/#heterogeneous-jobs
    """

    maintainers = ["k.stratford@epcc.ed.ac.uk"]
    descr = "SLURM hetjob for xthi shared MPI_COM_WORLD"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["*"]
    modules = ["xthi"]

    # Utter, utter kludge
    # 1 + 2 nodes; 8 + 2x4 MPI tasks
    hetgroup0 = "--het-group=0 --nodes=1 --ntasks=8 --ntasks-per-node=8 xthi"
    hetgroup1 = "--het-group=1 --nodes=2 --ntasks=8 --ntasks-per-node=4 xthi"
    executable = hetgroup0 + " : " + hetgroup1

    time_limit = "2m"
    # Kludge three nodes because we can't set the number of nodes explicitly
    num_tasks = 3
    num_tasks_per_node = 1
    env_vars = {"OMP_PLACES": "cores"}
    extra_resources = {"qos": {"qos": "standard"}}

    @sanity_function
    def sanity_check_run(self):
        """Ensure xthi ran successfully"""
        return sn.assert_found("Node summary", self.stdout)


@rfm.simple_test
class SharedCommWorldWithOpenMPTest(rfm.RunOnlyRegressionTest):

    """
    SLURM hetjob with shared MPI_COMM_WORLD and OpenMP as per
    the mixed MPI/OpenMP example at
    https://docs.archer2.ac.uk/user-guide/scheduler/#heterogeneous-jobs
    """

    descr = "SLURM hetjob for shared MPI_COM_WORLD with OpenMP"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["*"]
    modules = ["xthi"]

    # Two nodes with 8 MPI tasks per node
    shared_args = " --nodes=1 --ntasks=8 --tasks-per-node=8 --cpus-per-task=16"
    openmp0 = " --export=all,OMP_NUM_THREADS=16"
    openmp1 = " --export=all,OMP_NUM_THREADS=1"
    hetgroup0 = "--het-group=0" + shared_args + openmp0 + " xthi"
    hetgroup1 = "--het-group=1" + shared_args + openmp1 + " xthi"
    executable = hetgroup0 + " : " + hetgroup1

    time_limit = "2m"

    # Kludge two nodes because we can't set the number of nodes explicitly
    num_tasks = 2
    num_tasks_per_node = 1

    env_vars = {"OMP_PLACES": "cores"}
    extra_resources = {"qos": {"qos": "standard"}}

    @run_before("run")
    def unset_omp_num_threads(self):
        """Ensure OMP_NUM_THREADS is unset"""
        self.prerun_cmds = ["unset OMP_NUM_THREADS"]

    @sanity_function
    def sanity_check_run(self):
        """Ensure xthi ran successfully"""
        return sn.assert_found("Node summary", self.stdout)
