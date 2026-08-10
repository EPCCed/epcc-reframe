#!/usr/bin/env python3
"""ReFrame test for VASP CdTe benchmark."""

import reframe as rfm
import reframe.utility.sanity as sn


VASP_BENCHMARK_DIR = "/work/z19/z19/lparisi/2026-06_NCR-expansion-9Jul2026/VASP/CdTe/6.5.1_GCC13_LibSci-OFI"


@rfm.simple_test
class VASPCdTeCheck(rfm.RunOnlyRegressionTest):
    """VASP CdTe correctness and performance check."""

    descr = "VASP CdTe benchmark run"
    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    modules = ["vasp/6/6.5.1"]

    executable = "vasp_ncl"

    num_nodes = 4
    num_tasks_per_node = 144
    num_cpus_per_task = 2
    num_tasks = num_nodes * num_tasks_per_node
    time_limit = "20m"

    use_multithreading = False
    tags = {"applications", "performance", "small"}
    keep_files = ["OUTCAR", "INCAR"]

    env_vars = {
        "OMP_NUM_THREADS": "1",
        "OMP_PLACES": "cores",
        "SRUN_CPUS_PER_TASK": str(num_cpus_per_task),
    }

    reference = {
        "cirrus-ex:compute": {
            "performance": (651.0, -0.05, 0.05, "seconds"),
        }
    }

    @run_before("run")
    def setup_case(self):
        """Prepare the VASP input files and INCAR settings."""
        self.job.launcher.options = ["--hint=nomultithread", "--distribution=block:block"]
        self.prerun_cmds = [
            "cd CdTe",
            "mv INCAR.base INCAR",
            "cat $VASP_PSPOT_DIR/potpaw_PBE/Cd/POTCAR  $VASP_PSPOT_DIR/potpaw_PBE/Te/POTCAR > POTCAR",
            "echo 'NCORE=4' >> INCAR",
            "echo 'KPAR=2' >> INCAR",
        ]

    @sanity_function
    def assert_finished(self):
        """Sanity check that VASP completed and printed timing."""
        return sn.all(
            [
                sn.assert_found(r"General timing and accounting informations for this job:", "CdTe/OUTCAR"),
                sn.assert_found(r"Elapsed time \(sec\):", "CdTe/OUTCAR"),
            ]
        )

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract elapsed runtime from OUTCAR."""
        return sn.extractsingle(r"Elapsed time \(sec\):\s+(?P<runtime>\S+)", "CdTe/OUTCAR", "runtime", float)
