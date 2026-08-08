"""ReFrame test for OpenFOAM 3D lid-driven cavity."""

import reframe as rfm
import reframe.utility.sanity as sn

from openfoam_org_base import OpenFOAMBase


class OpenFOAMCavity3DBase(OpenFOAMBase):
    """OpenFOAM 3D lid-driven cavity base test."""

    valid_systems = ["cirrus-ex:compute"]
    
    num_cpus_per_task = 1
    time_limit = "20m"

    @run_before("run")
    def setup_tasks(self):
        self.num_tasks_per_node = self.current_partition.processor.num_cpus
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

    @sanity_function
    def assert_finished(self):
        """Check that the solver completed successfully."""
        return sn.all([sn.assert_found("End", self.stdout), sn.assert_found("Finalising parallel run", self.stdout)])

    @performance_function("seconds", perf_key="performance")
    def extract_perf(self):
        """Extract the final execution time from the solver output."""
        return sn.extractsingle(
            r"ExecutionTime\s+=\s+(?P<time>\d+\.\d+)\s+s\s+ClockTime\s+=\s+\d+\s+s\n\nEnd",
            self.stdout,
            "time",
            float,
        )

    @run_before("run")
    def setup_testcase(self):
        """Prepare to run OpenFoam in parallel, by performance the mesh decomposition and partitioning."""
        
        self.prerun_cmds = [
            "cd cavity_3d",
            "blockMesh",
            f"cp system/decomposeParDict{self.num_tasks:04.0f}  system/decomposeParDict",
            "decomposePar -force -fileHandler collated"
        ]

    modules = ["openfoam-org"]

    @run_before("performance")
    def set_reference(self):
        """Set the reference performance for Cirrus."""
        self.reference["cirrus-ex:compute:performance"] = self.reference_performance_cirrus_ex

@rfm.simple_test
class OpenFOAMCavity3D4Node(OpenFOAMCavity3DBase):
    """OpenFOAM 3D lid-driven cavity test on four nodes."""
    
    num_nodes = 4
    executable = "icoFoam"
    executable_opts = ["-parallel", "-fileHandler", "collated"]

    reference_performance_cirrus_ex = (78, -0.2, 0.1, "seconds")