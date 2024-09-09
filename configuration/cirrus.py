"""Cirrus Settings"""

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
                    "environs": ["Default", "gcc", "intel"],
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
                    "environs": ["gcc", "intel"],
                    "resources": [
                        {
                            "name": "qos",
                            "options": ["--qos={qos}"],
                        },
                    ],
                    "processor": {
                        "num_cpus": 36,
                        "num_cpus_per_socket": 18,
                        "num_sockets": 2,
                    }
                },
                {
                    "name": "highmem",
                    "descr": "High memory compute nodes",
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--hint=nomultithread",
                        "--distribution=block:block",
                        "--partition=highmem",
                    ],
                    "max_jobs": 16,
                    "environs": ["gcc", "intel"],
                    "resources": [
                        {
                            "name": "qos",
                            "options": ["--qos=highmem"],
                        },
                    ],
                    "processor": {
                        "num_cpus": 112,
                        "num_cpus_per_socket": 28,
                        "num_sockets": 4,
                    }
                },
                {
                    "name": "compute-gpu",
                    "descr": "Compute nodes with GPUs",
                    "features": ["gpu"],
                    "scheduler": "slurm",
                    "launcher": "srun",
                    "access": [
                        "--partition=gpu",
                    ],
                    "max_jobs": 4,
                    "environs": ["Default", "nvidia-mpi"],
                    "resources": [
                        {"name": "qos", "options": ["--qos={qos}"]},
                        {
                            "name": "gpu",
                            "options": ["--gres=gpu:{num_gpus_per_node}"],
                        },
                    ],
                    "processor": {
                        "num_cpus": 40,
                        "num_cpus_per_socket": 20,
                        "num_sockets": 2,
                    },
                    "devices": [
                        {"type": "gpu", "num_devices": 4}
                    ]
                },
            ],
        }
    ],
    "environments": [
        {
            "name": "gcc",
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
            "modules": ["nvidia/nvhpc-nompi/22.2", "openmpi/4.1.6-cuda-11.8"],
            "features": ["gpu"],
            "cc": "nvcc",
            "cxx": "nvcc",
            "ftn": "nvfortran",
            "target_systems": ["cirrus:compute-gpu"],
        },
        {
            "name": "Default",
            "cc": "gcc",
            "cxx": "gcc",
            "ftn": "gfortran",
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
