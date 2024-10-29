"""ReFrame base module for applications tests"""

import reframe as rfm
import reframe.utility.sanity as sn
import abc



@rfm.simple_test
class AppsFetchBase(rfm.RunonlyRegressionTest):
    """Reframe base class for accessing application code"""
    descr = 'Fetch app code'
    version = variable(str, value='7.3')
    executable = 'wget'
    executable_opts = [
        f'app-{version}'
    ]
    local = True
    valid_systems = ['']
    valid_prog_environs = ['']

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


@rfm.simple_test
class AppsCompileBase(rfm.CompileOnlyRegressionTest, metaclass=abc.ABCMeta):
    """Reframe base class for application compilation tests"""
    descr = 'Build app'
    build_system = ''
    valid_systems = ['']
    valid_prog_environs = ['']

    @abc.abstractmethod
    @run_after('init')
    def add_dependencies(self):
        self.depends_on('', udeps.fully)

    @sanity_function
    def validate_compilation_no_errors(self):
        """Sanity check that software compiled correctly"""
        return sn.assert_eq(self.job.exitcode, 0)

    @abc.abstractmethod
    @sanity_function
    def validate_compilation_executable_produced(self):
        """Sanity check that software compiled correctly"""
        pass


@rfm.simple_test
class AppsRunBase(rfm.RunOnlyRegressionTest, metaclass=abc.ABCMeta):
    """ReFrame base class for applications execution tests"""

    # Test classifications 
    tags = {""} # { "applications", "performance", "largescale", "hugescale"}

    # Test environments
    valid_prog_environs = [""]
    
    #Test executables 
    executable = ""

    #
    extra_resources = {""} # {"qos": {"qos": "standard"}}
    strict_check = True

    # Depency
    appbinary = fixture(AppsCompileBase, scope="environment")

    # Outputs
    keep_files = [""]

    # Info
    maintainers =[""]


    # Sanity checks

    @sanity_function
    def validate_run_finished_no_error(self) -> bool:
        """Sanity check that simulation finished successfully"""
        return sn.assert_eq(self.job.exitcode, 0)

    @abc.abstractmethod
    @sanity_function
    def validate_run_finished(self) -> bool:
        """Sanity check that simulation finished successfully"""
        pass
    
    @abc.abstractmethod
    @sanity_function
    def assert_correctness(self) -> bool:
        """Sanity check that simulation finished correctly"""
        pass

    # Application performance check

    @abc.abstractmethod
    @performance_function("app", perf_key="performance")
    def extract_performance(self):
        """Extract performance value to compare with reference value"""
        #return sn.extractsingle("","")
        pass


    # Job performance tests

    @performance_function("J", perf_key="job_energy")
    def extract_job_energy(self):
        """Extract value of energy used in job from slurm"""
        jobid = self.job.jobid
    
        slurm = rfm.utility.osext.run_command(
            "sacct -j " + str(jobid) + " --format=JobID,ConsumedEnergy --noconvert | tr '\n' ' ' ",
            check=True,
            shell=True,
        )

        energy_slurm = sn.extractall_s(
            r"JobID\s+ConsumedEnergy\s+------------ --------------\s+[0-9]+\s+[0-9]+\s+[0-9]+.bat\+\s+[0-9]+\s+[0-9]+.ext\+\s+[0-9]+\s+[0-9]+.0\s+(?P<energy>[0-9]+)",
            str(slurm.stdout),
            "energy",
        )
        return int(str(energy_slurm[0]))

    @performance_function("sec", perf_key="job_time")
    def extract_job_time(self):
        """Extract value of the duration of the job from slurm"""
        return self.completion_time


