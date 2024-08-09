import reframe as rfm
from reframe.core.builtins import run_after, variable

from namd_base import NAMDBase, NAMDNoSMPMixin, NAMDGPUMixin


class NAMDStmvBase(NAMDBase):
    """ReFrame NAMD stmv (1M atoms) test base class"""

    valid_systems = ["cirrus:compute", "cirrus:highmem"]
    descr = "NAMD stmv (1M atoms) performance"
    input_file = "stmv.namd"
    time_limit = "10m"

    energy_reference = -2451700.0

    reference = {
        "archer2:compute": {
            "energy": (energy_reference, -0.005, 0.005, "kcal/mol"),
        },
        "archer2-tds:compute": {
            "energy": (energy_reference, -0.005, 0.005, "kcal/mol"),
        },
        "cirrus:compute": {
            "energy": (energy_reference, -0.005, 0.005, "kcal/mol"),
        },
        "cirrus:highmem": {
            "energy": (energy_reference, -0.005, 0.005, "kcal/mol"),
        },
        "cirrus:compute-gpu": {
            "energy": (energy_reference, -0.005, 0.005, "kcal/mol"),
        },
    }

    n_nodes = variable(
        dict,
        value={
            "archer2:compute": 4,
            "archer2-tds:compute": 4,
            "cirrus:compute": 4,
            "cirrus:compute-gpu": 1,
            "cirrus:highmem": 1,
        },
    )

    @run_after("setup")
    def setup_resources(self):
        self.num_nodes = self.n_nodes[self.current_partition.fullname]
        super().setup_resources()


@rfm.simple_test
class NAMDStmvCPU(NAMDStmvBase):

    descr = NAMDStmvBase.descr + " -- CPU"

    reference["cirrus:compute:performance"] = (
        0.389,
        -0.05,
        0.05,
        "ns/day",
    )
    reference["cirrus:highmem:performance"] = (
        0.371,
        -0.05,
        0.05,
        "ns/day",
    )


@rfm.simple_test
class NAMDStmvCPUNoSMP(NAMDStmvBase, NAMDNoSMPMixin):

    descr = NAMDStmvBase.descr + " -- CPU, No SMP"

    reference["cirrus:compute:performance"] = (
        0.407,
        -0.05,
        0.05,
        "ns/day",
    )

    reference["cirrus:highmem:performance"] = (
        0.377,
        -0.05,
        0.05,
        "ns/day",
    )


@rfm.simple_test
class NAMDStmvGPU(NAMDStmvBase, NAMDGPUMixin):

    valid_systems = ["cirrus:compute-gpu"]
    descr = NAMDStmvBase.descr + " -- GPU"

    gpus_per_node = 4
    qos = "short"

    reference["cirrus:compute-gpu:performance"] = (
        4.92,
        -0.05,
        0.05,
        "ns/day",
    )
