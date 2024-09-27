#!/usr/bin/env python3
"""Reframe test to check that CPU target environment variable is correctly set"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SlurmEnergyTest(rfm.RunOnlyRegressionTest):
    """Checks the energy reporting with a delay"""

    descr = "Checks whether SLURM_CPU_FREQ_REQ is set to 2GHz by default"
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
