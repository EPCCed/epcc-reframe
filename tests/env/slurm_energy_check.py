#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
import numpy as np

@rfm.simple_test
class SlurmEnergy1nodeTest(rfm.RunOnlyRegressionTest):
    """Checks the energy reporting with a delay"""

    descr = "Checks whether slurm collects the energy usage of jobs correctly"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    executable = "./energy_diff.sh"

    tags = {"production", "maintenance", "craype"}

    reference = {"archer2:compute": {"energy diff": (0, -1, 1, "jouls")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that SLURM_CPU_FREQ_REQ is set"""
        return sn.assert_found(f"\S+ J \S+ us", self.stdout)

    @performance_function("energy diff", perf_key="performance")
    def extract_perf(self):
        """Extract energy from counters to compare with slurm and check diff is zero"""
        jobid = self.job.jobid
        #print("jobid: ", jobid)
        slurm = rfm.utility.osext.run_command(
            "sacct -j " + str(jobid) + " --format=JobID,ConsumedEnergy --noconvert | tr '\n' ' ' ",
            check=True,
            shell=True,
        )
        # print("slurm: ", slurm.stdout)

        energy_counters = sn.extractall(r"(?P<energy>[0-9]+)\sJ\s(?P<time>[0-9]+)\sus", self.stdout, "energy")

        # print("energy counters: ", energy_counters)

        energy_slurm = sn.extractall_s(
            r"JobID\s+ConsumedEnergy\s+------------ --------------\s+[0-9]+\s+[0-9]+\s+[0-9]+.bat\+\s+[0-9]+\s+[0-9]+.ext\+\s+[0-9]+\s+[0-9]+.0\s+(?P<energy>[0-9]+)",
            str(slurm.stdout),
            "energy",
        )
        # print("energy slurm: ", energy_slurm)

        energy_counters_diff = int(str(energy_counters[1])) - int(str(energy_counters[0]))

        # print("energy counters diff: ", energy_counters_diff)

        diff = energy_counters_diff - int(str(energy_slurm[0]))

        # print("diff: ", diff)

        return diff



@rfm.simple_test
class SlurmEnergy4nodesTest(rfm.RunOnlyRegressionTest):
    """Checks the energy reporting with a delay"""

    descr = "Checks whether slurm collects the energy usage of jobs correctly"
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    executable = "./energy_diff_multi.sh"

    num_nodes = 4
    num_tasks_per_node = 1
    num_tasks = num_nodes * num_tasks_per_node
    

    tags = {"production", "maintenance", "craype"}

    reference = {"archer2:compute": {"energy diff": (0, -1, 1, "jouls")}}

    @sanity_function
    def assert_finished(self):
        """Sanity check that SLURM_CPU_FREQ_REQ is set"""
        return sn.assert_found(f"", self.stdout)

    @performance_function("energy diff", perf_key="performance")
    def extract_perf(self):
        """Extract energy from counters to compare with slurm and check diff is zero"""
        jobid = self.job.jobid
        #print("jobid: ", jobid)
        slurm = rfm.utility.osext.run_command(
            "sacct -j " + str(jobid) + " --format=JobID,ConsumedEnergy --noconvert | tr '\n' ' ' ",
            check=True,
            shell=True,
        )
        print("slurm: ", slurm.stdout)

        nodelist_raw = rfm.utility.osext.run_command(
            "ls nid* | tr '\n' ',' | sed 's/,$//g'",
            check=True,
            shell=True,
        )

        #print("nodelist output: ", nodelist_raw.stdout)

        nodelist = list(nodelist_raw.stdout.split(","))

        #print("nodelist: ", nodelist)

        energy_data = []

        energy_counters = []

        for i, nodeid in enumerate(nodelist):
            energy_data.append(sn.extractall(r"(?P<energy>[0-9]+)\sJ\s(?P<time>[0-9]+)\sus", nodeid , "energy"))

        for i, energy in enumerate(energy_data):
            energy_counters.append(int(str(energy[0])))
            energy_counters.append(int(str(energy[1])))

        #print("energy counters: ", energy_counters)

        energy_slurm = sn.extractall_s(
            r"JobID\s+ConsumedEnergy\s+------------ --------------\s+[0-9]+\s+[0-9]+\s+[0-9]+.bat\+\s+[0-9]+\s+[0-9]+.ext\+\s+[0-9]+\s+[0-9]+.0\s+(?P<energy>[0-9]+)",
            str(slurm.stdout),
            "energy",
        )
        #print("energy slurm: ", energy_slurm)

        energy_counters_diff = 0

        for i in np.arange(0, len(energy_counters), 2):
            print(energy_counters[i+1] - energy_counters[i])
            energy_counters_diff+=energy_counters[i+1] - energy_counters[i] 

        #print("energy counters diff: ", energy_counters_diff)

        diff = energy_counters_diff - int(str(energy_slurm[0]))

        #print("diff: ", diff)

        return diff
