site_configuration = {
    'systems': [
        {
            'name': 'cirrus',
            'descr': 'Cirrus',
            'hostnames': ['cirrus-login1','cirrus-login2','cirrus-login3'],
            'modules_system': 'tmod4',
            'partitions': [
                {
                    'name': 'login',
                    'descr': 'Login nodes',
                    'scheduler': 'local',
                    'launcher': 'local',
                    'environs': ['gnu','gnumpi','intel','intelmpi'],
                },
                {
                   'name': 'compute',
                   'descr': 'Compute nodes',
                   'scheduler': 'slurm',
                   'launcher': 'srun',
                   'access': ['--hint=nomultithread','--distribution=block:block','--partition=standard'],
                   'max_jobs': 16,
                   'environs': ['gnu','gnumpi','intel','intelmpi'],
                   'resources': [
                       {
                           'name': 'qos',
                           'options': ['--qos={qos}']
                       },
                   ]
                },
            ]
        }
    ],
    'environments': [
        {
            'name': 'gnu',
            'modules': ['gcc'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'target_systems': ['cirrus']
        },
        {
            'name': 'gnumpi',
            'modules': ['gcc','mpt'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'target_systems': ['cirrus']
        },

        {
           'name': 'intel',
           'modules': ['intel-20.4/compilers'],
           'cc': 'icc',
           'cxx': 'icpc',
           'ftn': 'ifort',
           'target_systems': ['cirrus']
       },
        {
            'name': 'intelmpi',
            'modules': ['mpt','intel-20.4/compilers'],
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpif90',
            'target_systems': ['cirrus']
        },

    ],
}
