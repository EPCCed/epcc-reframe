"""reframe script for lammps ethanol test"""
import reframe as rfm
import reframe.utility.sanity as sn


class LAMMPSBaseCheck(rfm.RunOnlyRegressionTest):
    def __init__(self, output_file):
        super().__init__()

        self.valid_prog_environs = ["PrgEnv-gnu",'intel']
        self.executable = "lmp"

        self.keep_files = [output_file]

        energy = sn.extractsingle(
            r"\s+11000\s+\S+\s+\S+\s+(?P<energy>\S+)",
            output_file,
            "energy",
            float,
            item=-1,
        )
        energy_reference = 537394.35

        self.sanity_patterns = sn.all(
            [
                sn.assert_found("Total wall time", output_file),
                sn.assert_reference(energy, energy_reference, -0.01, 0.01),
            ]
        )

        self.perf_patterns = {
            "perf": sn.extractsingle(
                r"Performance:\s+(?P<perf>\S+)", output_file, "perf", float
            ),
        }

        self.maintainers = ["a.turner@epcc.ed.ac.uk"]
        self.strict_check = False
        self.use_multithreading = False
        self.extra_resources = {"qos": {"qos": "standard"}}
        self.tags = {"applications", "performance", "largescale"}

# Needed to be renamed as was conflicting with test of same name in dipole_large.py
@rfm.simple_test
class LAMMPSARCHER2LargeCheckEthanol(LAMMPSBaseCheck):
    def __init__(self):
        super().__init__("log.lammps")

        self.valid_systems = ["archer2:compute"]
        self.descr = "LAMMPS large scale performance test"
        self.executable_opts = ["-i in.ethanol"]

        self.modules = ["lammps"]
        self.num_tasks = 128 * 4
        self.num_tasks_per_node = 128
        self.num_cpus_per_task = 1
        self.time_limit = "20m"
        self.env_vars = {"OMP_NUM_THREADS": str(self.num_cpus_per_task)}

        self.reference = {
            "archer2:compute": {
                "perf": (8.627, -0.1, 0.1, "ns/day"),
            }
        }
