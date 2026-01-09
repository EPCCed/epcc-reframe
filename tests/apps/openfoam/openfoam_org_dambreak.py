"""ReFrame test for OpenFOAM DamBreak"""

import os
import reframe as rfm
import reframe.utility.sanity as sn

from openfoam_org_base import OpenFOAMBase
from openfoam_org_build import CompileOpenFOAM



class OpenFOAMDamBreakBase(OpenFOAMBase):
    """OpenFOAM DamBreak test base class"""

    num_tasks_per_node = 1
    time_limit = "10m"
    valid_systems = ["archer2:compute"]
    
    @run_after("init")
    def setup_params(self):
        """sets up extra parameters"""

       


        if self.current_system.name in ["archer2"]:
            freq = parameter(["2250000", "2000000"])
        if self.current_system.name in ["archer2"]:
            self.env_vars = {
                "OMP_NUM_THREADS": str(self.num_cpus_per_task),
                "OMP_PLACES": "cores",
                "SLURM_CPU_FREQ_REQ": self.freq,
            }
        
        if self.current_system.name in ["cirrus-ex"]:
            self.env_vars.update(
            {"FOAM_INSTALL_DIR": "$FOAM_ETC/.."}
                                 )
            

    @run_before("run")
    def set_num_tasks(self):
        """Sets number of tasks"""
        if self.current_system.name in ["archer2"]:
            self.num_cpus_per_task = 128
            self.num_tasks_per_node = 1
            self.num_tasks = self.num_tasks_per_node * self.num_nodes
        elif self.current_system.name in ["cirrus-ex"]:
            self.num_cpus_per_task = 288
            self.num_tasks_per_node = 1
            self.num_tasks = self.num_tasks_per_node * self.num_nodes

    @run_before("run")
    def setup_testcase(self):
        """set up test case"""

        if (self.version.startswith("10")):
            tutorial_sub_dir="tutorials/multiphase/interFoam/laminar/damBreak/damBreak"
        else:
            if (self.version.startswith("12")):
                tutorial_sub_dir="tutorials/incompressibleVoF/damBreak"
            else:
                raise ValueError("Unsupported OpenFOAM version")
        
        
        self.prerun_cmds = [
            "source ${FOAM_INSTALL_DIR}/etc/bashrc",
            f"cp -r $FOAM_INSTALL_DIR/{tutorial_sub_dir} .",
            "cd damBreak",
            "blockMesh",
            "cp 0/alpha.water.orig 0/alpha.water",
            "setFields",
            "which interFoam",
        ]

    @run_before("performance")
    def set_reference(self):
        """Changes reference values"""
        if self.current_system.name in ["archer2"]:
            # https://reframe-hpc.readthedocs.io/en/stable/utility_functions_reference.html#reframe.utility.ScopedDict
            self.reference["archer2:compute:performance"] = self.reference_performance_archer2[self.freq]
        
        elif self.current_system.name in ["cirrus-ex"]:
            self.reference["cirrus-ex:compute:performance"] = self.reference_performance_cirrus_ex
        

class OpenFOAMDamBreakOneNode(OpenFOAMDamBreakBase):
    """OpenFOAM DamBreak base test on 1 node"""

    executable = "interFoam"
    executable_opts = ("").split()
    valid_systems = ["archer2:compute"]
    
    num_tasks = 1
    num_nodes = 1

    reference_performance_archer2 = {
        "2000000": (6, -0.1, 0.1, "seconds"),
        "2250000": (3.6, -0.1, 0.1, "seconds"),
    }

    reference_performance_cirrus_ex = (3, -0.5, 0.5, "seconds")


@rfm.simple_test
class OpenFOAMDamBreakOneNodeModule(OpenFOAMDamBreakOneNode):
    """OpenFOAM DamBreak test on 1 node with module"""
    valid_systems = ["archer2:compute","cirrus-ex:compute"]

    executable = "interFoam"

    @run_before("run")
    def load_modules(self):
        if self.current_system.name in ["archer2"]:
            self.modules = [f"openfoam/org/v{OpenFOAMBase.version}"]
        elif self.current_system.name in ["cirrus-ex"]:
            self.modules = [f"openfoam-org"]
    

@rfm.simple_test
class OpenFOAMDamBreakOneNodeBuild(OpenFOAMDamBreakOneNode):
    """OpenFOAM DamBreak test on 1 node with reframe source build"""

    interfoam_binary = fixture(CompileOpenFOAM, scope="environment")

    @run_after("setup")
    def setup_extra_params(self):
        """sets up extra parameters"""
        super().setup_params()
        self.env_vars.update(
            {"FOAM_INSTALL_DIR": os.path.join(self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}")}
        )

    @run_after("setup")
    def set_executable(self):
        """Sets up executable"""
        self.executable = os.path.join(
            self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}/platforms/crayGccDPInt32Opt/bin/interFoam"
        )


class OpenFOAMDamBreakParallel(OpenFOAMDamBreakBase):
    """OpenFOAM DamBreak base test on 4 nodes"""

    num_nodes = 4
    executable_opts = ("-parallel").split()

    reference_performance_archer2 = {
        "2000000": (5, -0.5, 0.5, "seconds"),
        "2250000": (5, -0.5, 0.5, "seconds"),
    }

    reference_performance_cirrus_ex = (5, -0.5, 0.5, "seconds")    

    @run_before("run")
    def setup_testcase(self):
        """Set up test case"""
        super().setup_testcase()
        self.prerun_cmds = [*self.prerun_cmds, 
            "cp -r ../decomposeParDict system",
        "decomposePar"]

    @sanity_function
    def assert_finished_parallel(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("Finalising parallel run", self.stdout)


@rfm.simple_test
class OpenFOAMDamBreakParallelModule(OpenFOAMDamBreakParallel):
    """OpenFOAM DamBreak test on 4 nodes with module"""
    
    valid_systems = ["archer2:compute","cirrus-ex:compute"]

    
    executable = "interFoam"
    @run_before("run")
    def load_modules(self): 
        if  self.current_system.name in ["archer2"]:
            self.modules = [f"openfoam/org/v{OpenFOAMBase.version}"]
        elif self.current_system.name in ["cirrus-ex"]:
            self.modules = [f"openfoam-org"]
    


@rfm.simple_test
class OpenFOAMDamBreakParallelBuild(OpenFOAMDamBreakParallel):
    """OpenFOAM DamBreak test on 4 nodes with reframe source build"""

    interfoam_binary = fixture(CompileOpenFOAM, scope="environment")

    @run_after("setup")
    def setup_extra_params(self):
        """sets up extra parameters"""
        super().setup_params()
        self.env_vars.update(
            {"FOAM_INSTALL_DIR": os.path.join(self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}")}
        )

    @run_after("setup")
    def set_executable(self):
        """Sets up executable"""
        self.executable = os.path.join(
            self.interfoam_binary.stagedir, f"OpenFOAM-{OpenFOAMBase.v_major}/platforms/crayGccDPInt32Opt/bin/interFoam"
        )
