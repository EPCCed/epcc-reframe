#
# ReFrame generic settings
#


class ReframeSettings:
    reframe_module = None
    job_poll_intervals = [1, 2, 3]
    job_submit_timeout = 60
    checks_path = ['checks/']
    checks_path_recurse = True

    site_configuration = {
        'systems': {
            'cirrus': {
                'descr': 'Cirrus',
                'hostnames': ['indy2'],
                'modules_system': 'tmod',
                'partitions': {
                    'login_ser': {
                        'scheduler': 'local',
                        'modules': [],
                        'access':  [],
                        'environs': ['PrgEnv-intel18', 'PrgEnv-intel17',
                                     'PrgEnv-gcc6'],
                        'descr': 'Login nodes: serial tests',
                        'max_jobs': 4
                    },
    
                    'compute_ser': {
                        'scheduler': 'pbs+local',
                        'modules': [],
                        'access':  ['-A z04'],
                        'environs': ['PrgEnv-intel18', 'PrgEnv-intel17', 'PrgEnv-gcc6'],
                        'descr': 'Compute nodes (Broadwell): serial jobs',
                        'max_jobs': 10
                    },

                    'compute_impi': {
                        'scheduler': 'pbs+mpirun',
                        'modules': [],
                        'access':  ['-A z04','-l place=scatter:excl'],
                        'environs': ['PrgEnv-intel18-impi', 'PrgEnv-intel17-impi', 'PrgEnv-gcc6-impi'],
                        'descr': 'Compute nodes (Broadwell): Intel MPI parallel jobs',
                        'max_jobs': 10
                    },

                    'compute_mpt': {
                        'scheduler': 'pbs+hpempt',
                        'modules': [],
                        'access':  ['-A z04','-l place=scatter:excl'],
                        'environs': ['PrgEnv-intel18-mpt', 'PrgEnv-intel17-mpt', 'PrgEnv-gcc6-mpt'],
                        'descr': 'Compute nodes (Broadwell): Intel MPI parallel jobs',
                        'max_jobs': 10
                    }
                }
            }
        },
    
        'environments': {
            '*': {
                'PrgEnv-intel17': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-17'],
                    'cc': 'icc',
                    'cxx': 'icpc',
                    'ftn': 'ifort',
                },
    
                'PrgEnv-intel18': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-18/18.0.5.274'],
                    'cc': 'icc',
                    'cxx': 'icpc',
                    'ftn': 'ifort',
                },
    
                'PrgEnv-gcc6': {
                    'type': 'ProgEnvironment',
                    'modules': ['gcc/6.3.0'],
                    'cc': 'gcc',
                    'cxx': 'g++',
                    'ftn': 'gfortran',
                },

                'PrgEnv-intel17-impi': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-17', 'intel-mpi-17'],
                    'cc': 'mpiicc',
                    'cxx': 'mpiicpc',
                    'ftn': 'mpiifort',
                },
    
                'PrgEnv-intel18-impi': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-18/18.0.5.274', 'intel-mpi-18'],
                    'cc': 'mpiicc',
                    'cxx': 'mpiicpc',
                    'ftn': 'mpiifort',
                },
    
                'PrgEnv-gcc6-impi': {
                    'type': 'ProgEnvironment',
                    'modules': ['gcc/6.3.0', 'intel-mpi-18'],
                    'cc': 'mpicc',
                    'cxx': 'mpicxx',
                    'ftn': 'mpif90',
                },

                'PrgEnv-intel17-mpt': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-17', 'mpt'],
                    'variables': {
                         'MPICC_CC': 'icc',
                         'MPICXX_CXX': 'icpc'
                    },
                    'cc': 'mpicc',
                    'cxx': 'mpicxx',
                    'ftn': 'mpif90',
                },
    
                'PrgEnv-intel18-mpt': {
                    'type': 'ProgEnvironment',
                    'modules': ['intel-tools-18/18.0.5.274', 'mpt'],
                    'variables': {
                         'MPICC_CC': 'icc',
                         'MPICXX_CXX': 'icpc'
                    },
                    'cc': 'mpicc',
                    'cxx': 'mpicxx',
                    'ftn': 'mpif90',
                },
    
                'PrgEnv-gcc6-mpt': {
                    'type': 'ProgEnvironment',
                    'modules': ['gcc/6.3.0', 'mpt'],
                    'cc': 'mpicc',
                    'cxx': 'mpicxx',
                    'ftn': 'mpif90',
                }
            }
        }
    }


    logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'file',
                'name': 'reframe.log',
                'level': 'DEBUG',
                'format': '[%(asctime)s] %(levelname)s: '
                          '%(check_info)s: %(message)s',
                'append': False,
            },

            # Output handling
            {
                'type': 'stream',
                'name': 'stdout',
                'level': 'INFO',
                'format': '%(message)s'
            },
            {
                'type': 'file',
                'name': 'reframe.out',
                'level': 'INFO',
                'format': '%(message)s',
                'append': False,
            }
        ]
    }

    perf_logging_config = {
        'level': 'DEBUG',
        'handlers': [
            {
                'type': 'filelog',
                'prefix': '%(check_system)s/%(check_partition)s',
                'level': 'INFO',
                'format': (
                    '%(asctime)s|reframe %(version)s|'
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


settings = ReframeSettings()
