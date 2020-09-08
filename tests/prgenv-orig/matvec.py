import reframe as rfm
import reframe.utility.sanity as sn


class BaseMatrixVectorTest(rfm.RegressionTest):
    def __init__(self, test_version):
        super().__init__()
        self.descr = '%s matrix-vector multiplication' % test_version
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.build_system = 'SingleSource'
        self.prgenv_flags = None

        matrix_dim = 1024
        iterations = 100
        self.executable_opts = [str(matrix_dim), str(iterations)]

        expected_norm = matrix_dim
        found_norm = sn.extractsingle(
            r'The L2 norm of the resulting vector is:\s+(?P<norm>\S+)',
            self.stdout, 'norm', float)
        self.sanity_patterns = sn.all([
            sn.assert_found(
                r'time for single matrix vector multiplication', self.stdout),
            sn.assert_lt(sn.abs(expected_norm - found_norm), 1.0e-6)
        ])
        self.maintainers = ['a.turner@epcc.ed.ac.uk']
        self.tags = {'prgenv'}

    def setup(self, partition, environ, **job_opts):
        if self.prgenv_flags is not None:
            self.build_system.cflags = self.prgenv_flags[environ.name]

        super().setup(partition, environ, **job_opts)


@rfm.simple_test
class SerialTest(BaseMatrixVectorTest):
    def __init__(self):
        super().__init__('Serial')
        self.valid_systems = ['cirrus:login_ser','cirrus:compute_ser','tesseract:login_ser']
        self.sourcepath = 'matrix_vector_multiplication.c'


@rfm.simple_test
class OpenMPTest(BaseMatrixVectorTest):
    def __init__(self):
        super().__init__('OpenMP')
        self.sourcepath = 'matrix_vector_multiplication_openmp.c'
        self.valid_systems = ['cirrus:login_ser','cirrus:compute_ser','tesseract:login_ser']
        self.prgenv_flags = {
            'PrgEnv-gcc6': ['-fopenmp'],
            'PrgEnv-intel17': ['-qopenmp'],
            'PrgEnv-intel18': ['-qopenmp'],
        }
        self.variables = {
            'OMP_NUM_THREADS': '4'
        }


@rfm.simple_test
class MPITest(BaseMatrixVectorTest):
    def __init__(self):
        super().__init__('MPI')
        self.valid_systems = ['cirrus:compute_impi','cirrus:compute_mpt','tesseract:compute_impi']
        self.sourcepath = 'matrix_vector_multiplication_mpi_openmp.c'
        self.prgenv_flags = {
            'PrgEnv-gcc6-impi': ['-fopenmp'],
            'PrgEnv-intel17-impi': ['-qopenmp'],
            'PrgEnv-intel18-impi': ['-qopenmp'],
            'PrgEnv-gcc6-mpt': ['-fopenmp'],
            'PrgEnv-intel17-mpt': ['-qopenmp'],
            'PrgEnv-intel18-mpt': ['-qopenmp']
        }
        self.num_tasks = 8
        self.num_tasks_per_node = 2
        self.num_cpus_per_task = 4
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }

