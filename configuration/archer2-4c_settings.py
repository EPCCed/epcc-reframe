site_configuration = {
    'systems': [
        {
            'name': 'archer2',
            'descr': 'ARCHER2',
            'hostnames': ['uan','ln'],
            'modules_system': 'tmod4',
            'partitions': [
                {
                    'name': 'login',
                    'descr': 'Login nodes',
                    'scheduler': 'local',
                    'launcher': 'local',
                    'environs': ['gnu','cray','amd'],
                },
                {
                    'name': 'compute',
                    'descr': 'Compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'srun',
#                    'access': ['--partition=standard','--qos=standard','--distribution=block:block'],
                    'access': ['--hint=nomultithread','--distribution=block:block'],
                    'environs': ['gnu', 'cray', 'amd'],
                    'max_jobs': 16
                }
            ]
        }
    ],
    'environments': [
        {
            'name': 'gnu',
            'modules': [
                {
                    'name': '/etc/cray-pe.d/PrgEnv-gnu',
                    'path': '/etc/cray-pe.d/PrgEnv-gnu',
                    'collection': True
                }
            ],
            'cc': 'cc',
            'cxx': 'CC',
            'ftn': 'ftn',
            'target_systems': ['archer2']
        },
        {
            'name': 'cray',
            'modules': [
                {
                    'name': '/etc/cray-pe.d/PrgEnv-cray',
                    'path': '/etc/cray-pe.d/PrgEnv-cray',
                    'collection': True
                }
            ],
            'cc': 'cc',
            'cxx': 'CC',
            'ftn': 'ftn',
            'target_systems': ['archer2']
        },
        {
            'name': 'amd',
            'modules': [
                {
                    'name': '/etc/cray-pe.d/PrgEnv-aocc',
                    'path': '/etc/cray-pe.d/PrgEnv-aocc',
                    'collection': True
                }
            ],
            'cc': 'cc',
            'cxx': 'CC',
            'ftn': 'ftn',
            'target_systems': ['archer2']
        },
    ],
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s'
                },
                {
                    'type': 'file',
                    'name': 'reframe.log',
                    'level': 'debug',
                    'format': '[%(asctime)s] %(levelname)s: %(check_info)s: %(message)s',   # noqa: E501
                    'append': False
                }
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': (
                        '%(check_job_completion_time)s|reframe %(version)s|'
                        '%(check_info)s|jobid=%(check_jobid)s|'
                        '%(check_perf_var)s=%(check_perf_value)s|'
                        'ref=%(check_perf_ref)s '
                        '(l=%(check_perf_lower_thres)s, '
                        'u=%(check_perf_upper_thres)s)|'
                        '%(check_perf_unit)s'
                    ),
                    'append': True
                }
            ]
        }
    ],
}

