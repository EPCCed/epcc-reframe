"""ARCHER2 TDS settings"""

site_configuration = {
    "systems": [
        {
            "name": "archer2",
            "descr": "ARCHER2 TDS",
            "hostnames": ["uan", "ln", "dvn"],
            "modules_system": "lmod",
            "partitions": [
                {
                    "name": "login",
                    "descr": "Login nodes",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": ["PrgEnv-gnu", "PrgEnv-cray", "PrgEnv-aocc"],
                },
                {
                    "name": "compute",
                    "descr": "Compute nodes",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--partition=workq",
                        "--qos=normal",
                    ],
                    "environs": ["PrgEnv-gnu", "PrgEnv-cray", "PrgEnv-aocc"],
                    "max_jobs": 16,
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
            "target_systems": ["archer2"],
        },
        {
            "name": "PrgEnv-cray",
            "modules": ["PrgEnv-cray"],
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["archer2"],
        },
        {
            "name": "PrgEnv-aocc",
            "modules": ["PrgEnv-aocc"],
            "cc": "cc",
            "cxx": "CC",
            "ftn": "ftn",
            "target_systems": ["archer2"],
        },
    ],
    "logging": [
        {
            "level": "debug",
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
                    "format": "[%(asctime)s] %(levelname)s %(levelno)s: %(check_info)s: %(message)s",
                    "append": False,
                },
            ],
            "handlers_perflog": [
                {
                    "type": "file",
                    "name": "reframe_perf.out",
                    "level": "info",
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
