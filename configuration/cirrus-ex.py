"""ARCHER2 settings"""

from reframe.core.backends import register_launcher
from reframe.core.launchers import JobLauncher

@register_launcher("torchrun")
class TorchRunLauncher(JobLauncher):
    """Launcher for Torch run"""

    def command(self, job):
        return ["torchrun", "--nproc_per_node=4"]


site_configuration = {
    "systems": [
        {
            "name": "cirrus-ex",
            "descr": "Cirrus EX4000",
            "hostnames": ["login"],
            "modules_system": "lmod",
            "partitions": [
                {
                    "name": "login",
                    "descr": "Login nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": [
                        "Default",
                        "PrgEnv-gnu",
                        "PrgEnv-cray",
                        "PrgEnv-aocc",
                        "PrgEnv-intel"
                    ],
                },
                {
                    "name": "compute",
                    "descr": "Compute nodes",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--exclusive",
                        "--partition=standard",
                        "--qos=standard",
                    ],
                    "environs": [
                        "PrgEnv-gnu",
                        "PrgEnv-cray",
                        "PrgEnv-aocc",
                        "PrgEnv-intel"
                    ],
                    "max_jobs": 10,
                    "processor": {
                        "num_cpus": 288,
                        "num_cpus_per_socket": 144,
                        "num_sockets": 2,
                    },
                },
            ],
        }
    ],
    "environments": [
        {
            "name": "PrgEnv-gnu",
            "modules": ["PrgEnv-gnu"],
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["cirrus-ex"],
        },
        {
            "name": "PrgEnv-cray",
            "modules": ["PrgEnv-cray"],
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["cirrus-ex"],
        },
        {
            "name": "PrgEnv-aocc",
            "modules": ["PrgEnv-aocc"],
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["cirrus-ex"],
        },
        {
            "name": "PrgEnv-intel",
            "modules": ["PrgEnv-intel"],
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["cirrus-ex"],
        },
        {
            "name": "Default",
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["cirrus-ex"],
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
                    "format": ("[%(asctime)s] %(levelname)s %(levelno)s: %(check_info)s: %(message)s"),
                    "append": False,
                },
            ],
            "handlers_perflog": [
                {
                    "type": "file",
                    "name": "reframe_perf.out",
                    "level": "info",
                    "perflog_compat": True,
                    "format": (
                        "[%(asctime)s] %(check_info)s: %(check_perf_var)s=%(check_perf_value)s "
                        "(ref=%(check_perf_ref)s;l=%(check_perf_lower_thres)s;u=%(check_perf_upper_thres)s)) "
                        "%(check_perf_unit)s"
                    ),
                    "append": True,
                },
                {
                    "type": "filelog",
                    "prefix": "%(check_system)s/%(check_partition)s",
                    "level": "info",
                    "format": (
                        "%(check_display_name)s|%(check_result)s|%(check_job_completion_time)s|"
                        "%(check_perf_var)s|"
                        "%(check_perf_value)s %(check_perf_unit)s|"
                        "(%(check_perf_ref)s, %(check_perf_lower_thres)s, %(check_perf_upper_thres)s)|"
                    ),
                    "append": True,
                },
            ],
        }
    ],
}
