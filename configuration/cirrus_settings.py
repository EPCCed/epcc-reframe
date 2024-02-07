from reframe.core.backends import register_launcher
from reframe.core.launchers import JobLauncher

class ParamaterizedPatitionDict(dict):
    def __init__(self, num_gpus):
        super().__init__()
        if num_gpus <= 4:
            num_nodes = 1
        else:
            if num_gpus/4 - float(num_gpus//4) == 0:
                num_nodes = num_gpus//4
            else:
                num_nodes = num_nodes//4 + 1

        base_partition = {
            "name": f"compute-{num_gpus}-gpus",
            "descr": f"Compute nodes with {num_gpus} GPUs but doesn't load nvcc compilers or mpi",
            "scheduler": "slurm",
            "launcher" : "gpu_srun",
            "access": [
                "--partition=gpu",
                "--qos=gpu",
                "--exclusive",
                f"--nodes={num_nodes}"
                f"--gres=gpu:{num_gpus}"
                ],
            "environs": ["Default"]
        }

@register_launcher('gpu_srun')
class MultiGPULauncher(JobLauncher):
    def command(self, job):
        if job.num_tasks <=4:
            t_p_n = job.num_tasks
        else:
            t_p_n = 4
        return ['srun', f"--ntasks={job.num_tasks}", f"--tasks-per-node={t_p_n}"]

site_configuration = {
    "systems": [
        {
            "name": "cirrus",
            "descr": "Cirrus",
            "hostnames": ["cirrus-login1", "cirrus-login2", "cirrus-login3"],
            "modules_system": "tmod4",
            "partitions": [
                {
                    "name": "login",
                    "descr": "Login nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": ["gnu", "intel"],
                },
                {
                    "name": "compute",
                    "descr": "Compute nodes",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--partition=standard",
                    ],
                    "max_jobs": 16,
                    "environs": ["gnu", "intel"],
                    "resources": [
                        {
                            "name": "qos",
                            "options": ["--qos={qos}"],
                        },
                    ],
                },
                {
                    "name": "compute-gpu",
                    "descr": "Compute nodes with GPUs",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--partition=gpu",
                    ],
                    "max_jobs": 4,
                    "environs": ["nvidia-mpi"],
                    "resources": [
                        {"name": "qos", "options": ["--qos={qos}"]},
                        {
                            "name": "gpu",
                            "options": ["--gres=gpu:{num_gpus_per_node}"],
                        },
                    ],
                },
                {
                    "name": "compute-gpu-default",
                    "descr": "Compute nodes with GPUs but doesn't load nvcc compilers or mpi",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--partition=gpu",
                    ],
                    "max_jobs": 4,
                    "environs": ["Default"],
                    "resources": [
                        {"name": "qos", "options": ["--qos={qos}"]},
                    ],
                },
            ],
        }
    ],
    "environments": [
        {
            "name": "gnu",
            "modules": ["gcc", "mpt"],
            "cc": "mpicc",
            "cxx": "mpicxx",
            "ftn": "mpif90",
            "target_systems": ["cirrus"],
        },
        {
            "name": "intel",
            "modules": ["mpt", "intel-20.4/compilers"],
            "cc": "mpicc",
            "cxx": "mpicxx",
            "ftn": "mpif90",
            "target_systems": ["cirrus"],
        },
        {
            "name": "nvidia-mpi",
            "modules": ["nvidia/nvhpc-nompi/22.2", "openmpi/4.1.2-cuda-11.6"],
            "cc": "nvcc",
            "cxx": "nvcc",
            "ftn": "nvfortran",
            "target_systems": ["cirrus"],
        },
        {
            "name": "Default",
            "cc": "gcc",
            "target_systems": ["cirrus"],
        },
    ],
    "logging": [
        {
            "level": "debug",
            "perflog_compat": True,
            "handlers": [
                {
                    "type": "stream",
                    "name": "stdout",
                    "level": "info",
                    "format": "%(message)s",
                },
                {
                    "type": "file",
                    "name": "reframe.out",
                    "level": "info",
                    "format": "[%(asctime)s] %(check_info)s: %(message)s",
                    "append": True,
                },
                {
                    "type": "file",
                    "name": "reframe.log",
                    "level": "debug",
                    "format": (
                        "[%(asctime)s] %(levelname)s "
                        "%(levelno)s: %(check_info)s: %(message)s"
                    ),
                    "append": False,
                },
            ],
            "handlers_perflog": [
                {
                    "type": "file",
                    "name": "reframe_perf.out",
                    "level": "info",
                    "format": (
                        "[%(asctime)s] %(check_info)s: "
                        "%(check_perf_var)s=%(check_perf_value)s "
                        "(ref=%(check_perf_ref)s;l=%(check_perf_lower_thres)s;"
                        "u=%(check_perf_upper_thres)s)) %(check_perf_unit)s"
                    ),
                    "append": True,
                },
                {
                    "type": "filelog",
                    "prefix": "%(check_system)s/%(check_partition)s",
                    "level": "info",
                    "format": (
                        "%(check_job_completion_time)s|reframe %(version)s|"
                        "%(check_info)s|jobid=%(check_jobid)s|"
                        "%(check_perf_var)s=%(check_perf_value)s|"
                        "ref=%(check_perf_ref)s "
                        "(l=%(check_perf_lower_thres)s, "
                        "u=%(check_perf_upper_thres)s)|"
                        "%(check_perf_unit)s"
                    ),
                    "append": True,
                },
            ],
        }
    ],
}
