"""Reframe test to check that Slurm reports energy use"""

# Based on work from:
#   Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
#   ReFrame Project Developers. See the top-level LICENSE file for details.
#   SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SlurmEnergy1nodeTest(rfm.RunOnlyRegressionTest):
    """Checks the energy reporting with a delay"""

    descr = "Checks whether slurm collects the energy usage of jobs correctly"
    valid_systems = ["archer2:compute", "cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    executable = "./energy_diff.sh"

    tags = {"production", "maintenance", "craype"}

    reference = {
        "archer2:compute": {"energy-diff": (0, -1, 1, "J")},
        "cirrus-ex:compute": {"energy-diff": (0, -1, 1, "J")},
    }

    @sanity_function
    def assert_finished(self):
        """Sanity check that SLURM_CPU_FREQ_REQ is set"""
        return sn.assert_found(r"\S+ J \S+ us", self.stdout)

    @performance_function("J", perf_key="energy-diff")
    def extract_perf(self):
        """Extract energy from counters to compare with slurm and check diff is zero"""

        jobid = self.job.jobid
        slurm = rfm.utility.osext.run_command(
            "sacct -j " + str(jobid) + " --format=JobID,ConsumedEnergy --noconvert | tr '\n' ' ' ",
            check=True,
            shell=True,
        )

        # Extract counter energy, recorded in stdout
        energy_counters = sn.extractall(r"(?P<energy>[0-9]+)\sJ\s(?P<time>[0-9]+)\sus", self.stdout, "energy")

        # Extract energy from Slurm output
        energy_slurm = sn.extractall_s(r"ConsumedEnergy.*?\s+(?P<energy>[0-9]+)\s*$", str(slurm.stdout), "energy")

        # Difference in energy counters at start and end of job
        energy_counters_diff = int(str(energy_counters[1])) - int(str(energy_counters[0]))

        # Difference in counter recording and slurm output
        diff = energy_counters_diff - int(str(energy_slurm[0]))

        # Helpful debugging outputs:
        # print("jobid: ", jobid)
        # print("energy recorded by slurm: ", energy_slurm)
        # print("2x energy counter recordings: ", energy_counters)
        # print("Difference between the energy counters: ", energy_counters_diff)
        # print("difference between counters and slurm: ", diff)

        return diff


@rfm.simple_test
class SlurmEnergy4nodesTest(rfm.RunOnlyRegressionTest):
    """Checks the energy reporting with a delay"""

    descr = "Checks whether slurm collects the energy usage of jobs correctly"
    valid_systems = ["archer2:compute", "cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-cray"]
    executable = "./energy_diff_multi.sh"

    num_nodes = 4
    num_tasks_per_node = 1
    num_tasks = num_nodes * num_tasks_per_node

    tags = {"production", "maintenance", "craype"}

    reference = {
        "archer2:compute": {"energy-diff": (0, -1, 1, "J")},
        "cirrus-ex:compute": {"energy-diff": (0, -1, 1, "J")},
    }

    def get_energy(self):
        """Return energy from slurm and energy from counters"""
        jobid = self.job.jobid
        slurm = rfm.utility.osext.run_command(
            "sacct -j " + str(jobid) + " --format=JobID,ConsumedEnergy --noconvert | tr '\n' ' ' ",
            check=True,
            shell=True,
        )

        nodelist_raw = rfm.utility.osext.run_command(
            "ls cs-n* | tr '\n' ',' | sed 's/,$//g'",
            check=True,
            shell=True,
        )

        nodelist = list(nodelist_raw.stdout.split(","))
        energy_data = []
        energy_counters = []

        assert len(nodelist) == self.num_nodes, "Number of nodes in nodelist does not match number of nodes requested"

        for nodeid in nodelist:
            energy_data.append(sn.extractall(r"(?P<energy>[0-9]+)\sJ\s(?P<time>[0-9]+)\sus", nodeid, "energy"))

        print("Node list: ", nodelist_raw)
        for energy in energy_data:
            energy_counters.append(int(str(energy[0])))
            energy_counters.append(int(str(energy[1])))

        # Extract energy from Slurm output
        energy_slurm = sn.extractall_s(r"ConsumedEnergy.*?\s+(?P<energy>[0-9]+)\s*$", str(slurm.stdout), "energy")

        energy_counters_diff = 0

        for i in range(0, len(energy_counters), 2):
            # print(energy_counters[i + 1] - energy_counters[i])
            energy_counters_diff += energy_counters[i + 1] - energy_counters[i]

        return energy_counters_diff, int(str(energy_slurm[0]))

        # Helpful debugging outputs:
        # print("jobid: ", jobid)
        # print("nodelist output: ", nodelist_raw.stdout)
        # print("nodelist: ", nodelist)
        # print("energy recorded by slurm: ", energy_slurm)
        # print("2x energy counter recordings: ", energy_counters)
        # print("Difference between the energy counters: ", energy_counters_diff)
        # print("difference between counters and slurm: ", diff)

    @sanity_function
    def assert_energy_recorded(self):
        """Assert that the energy counters and slurm energy are greater than zero"""

        energy_counters_diff, energy_slurm = self.get_energy()

        return sn.assert_true(energy_counters_diff > 0) and sn.assert_true(energy_slurm > 0)

    @performance_function("J", perf_key="energy-diff")
    def extract_perf(self):
        """Extract relative energy difference between counters and slurm output"""

        energy_counters_diff, energy_slurm = self.get_energy()
        diff = (energy_counters_diff - energy_slurm) / energy_slurm

        return diff
