site_configuration = {
    'systems': {
        'cirrus': {
            'descr': 'Cirrus',
            'hostnames': ['cirrus'],
            'modules_system': 'tmod',
            'partitions': {
                'login': {
                    'scheduler': 'local',
                    'modules': [],
                    'access':  [],
                    'environs': ['PrgEnv-intel18-impi', 'PrgEnv-intel17-impi',
                                 'PrgEnv-gcc6-impi'],
                    'descr': 'Login nodes',
                    'max_jobs': 4
                },

                'compute': {
                    'scheduler': 'pbs+mpirun',
                    'modules': [],
                    'access':  [],
                    'environs': ['PrgEnv-intel18-impi', 'PrgEnv-intel17-impi',
                                 'PrgEnv-gcc6-impi'],
                    'descr': 'Compute nodes (Broadwell)',
                    'max_jobs': 10
                }
            }
        }
    },

    'environments': {
        '*': {
            'PrgEnv-intel17-impi': {
                'type': 'ProgEnvironment',
                'modules': ['intel-tools-17', 'intel-mpi-17'],
            },

            'PrgEnv-intel18-impi': {
                'type': 'ProgEnvironment',
                'modules': ['intel-tools-18', 'intel-mpi-18'],
            },

            'PrgEnv-gcc6-impi': {
                'type': 'ProgEnvironment',
                'modules': ['gcc/6.3.0', 'intel-mpi-18'],
            }
        }
    }
}
