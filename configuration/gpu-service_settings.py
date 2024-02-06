site_configuration = {
    "systems": [
        {
            "name": "gpu-service",
            "descr": "Edinburgh International Data Facility GPU-Service",
            "hostnames": ["gpu-service"],
            "partitions": [
                {
                    "name": "gpu-service",
                    "descr": "Edinburgh International Data Facility GPU-Service",
                    "scheduler": "local",
                    "launcher": "local",
                    "environs": ["Default"],
                }
            ],
        }
    ],
    "environments": [
        {
            "name": "Default",
            "target_systems": ["*"],
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
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': (
                        '%(check_display_name)s|%(check_result)s|%(check_job_completion_time)s|'
                        '%(check_perf_var)s|'
                        '%(check_perf_value)s %(check_perf_unit)s|'
                        '(%(check_perf_ref)s, %(check_perf_lower_thres)s, %(check_perf_upper_thres)s)|'
                    ),
                    
                    'append': True
                },
            ],
        }
    ],
}