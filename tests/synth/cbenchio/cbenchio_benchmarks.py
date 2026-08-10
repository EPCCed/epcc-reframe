from cbenchio import cbenchio_write, Parameterize, make_read_test


""" Cbenchio benchmarks

Contains I/O benchmarks based on cbenchio.

## Adding new tests

Add a new test by inherting from cbenchio_write and using the Parameterize metaclass. 
The class should have a config attribute pointing to a yaml file. 
The yaml file should contain the parameters for the test. For example:

```python
class cbenchio_bandwidth_write(cbenchio_write,metaclass=Parameterize):
    operation = "write"
    config= "posix.yaml"
```

Read tests can be generated from write tests using the make_read_test function. 
For instance we can generate a read test from the write test above using:

```python
cbenchio_bandwidth_read = make_read_test(cbenchio_bandwidth_write)
```

"""


class cbenchio_posix_sequential_write(cbenchio_write, metaclass=Parameterize):
    """Measure the bandwidth of the filesystem for file per process patterns for large sequential I/O."""

    operation = "write"
    config = "posix-sequential.yaml"
    fields = 1


cbenchio_posix_sequential_read = make_read_test(cbenchio_posix_sequential_write)


class cbenchio_posix_random_write(cbenchio_write, metaclass=Parameterize):
    """Measure the bandwidth of the filesystem for file per process patterns random 4KiB I/O."""

    operation = "write"
    config = "posix-random.yaml"
    random_strided = True
    fields = 4


cbenchio_posix_random_read = make_read_test(cbenchio_posix_random_write)


class cbenchio_mpi_1D_write(cbenchio_write, metaclass=Parameterize):
    """Ideal scaling of a 1D array with one task per node. This tests the ideal scaling of parallel writes to a single file."""

    operation = "write"
    config = "mpi-1D.yaml"
    file_per_process = False
    dimensions = 1
    fields = 4
    n_dimensions = 1
    stripe_size = 4194304


cbenchio_mpi_1D_read = make_read_test(cbenchio_mpi_1D_write)


class cbenchio_mpi_3D_write(cbenchio_write, metaclass=Parameterize):
    """Measure the bandwidth of the filesystem for a single file written by all processes in a 3D layout."""

    operation = "write"
    config = "mpi-3D.yaml"
    file_per_process = False
    dimensions = 3
    fields = 4
    n_dimensions = 3
    stripe_size = 4194304


cbenchio_mpi_3D_read = make_read_test(cbenchio_mpi_3D_write)
