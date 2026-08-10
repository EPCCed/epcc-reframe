"""Cbenchio benchmarks

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

from cbenchio import CbenchioWrite, make_read_test


class CbenchioPosixSequentialWrite(CbenchioWrite):
    """Measure the bandwidth of the filesystem for file per process patterns for large sequential I/O."""

    operation = "write"
    fields = 1
    nodes = parameter([1, 4, 8])
    tasks_per_node = parameter([288])
    base_path = parameter(["base_path"])
    chunk_size = parameter([1048576])
    field_size_per_process_per_dimension = parameter([1073741824])
    api = "posix"


CbenchioPosixSequentialRead = make_read_test(CbenchioPosixSequentialWrite)


class CbenchioPosixRandomWrite(CbenchioWrite):
    """Measure the bandwidth of the filesystem for file per process patterns random 4KiB I/O."""

    operation = "write"
    config = "posix-random.yaml"
    random_strided = True
    fields = 4

    nodes = parameter([1, 4, 8])
    tasks_per_node = parameter([288])
    base_path = parameter(["/work/z19/shared/io_benchmarks"])
    api = "posix"
    chunk_size = parameter([4096])
    field_size_per_process_per_dimension = parameter([65536])


CbenchioPosixRandomRead = make_read_test(CbenchioPosixRandomWrite)


class CbenchioMpi1DWrite(CbenchioWrite):
    """Ideal scaling of a 1D array with one task per node.
    This tests the ideal scaling of parallel writes to a single file.
    """

    operation = "write"
    file_per_process = False
    dimensions = 1
    fields = 4
    n_dimensions = 1
    stripe_size = 4194304

    nodes = parameter([1, 4, 8])
    tasks_per_node = parameter([1])
    base_path = parameter(["/work/z19/shared/io_benchmarks"])
    api = "mpi"
    stripes = parameter(["num_nodes"])
    field_size_per_process_per_dimension = parameter([1073741824])


CbenchioMpi1DRead = make_read_test(CbenchioMpi1DWrite)


class CbenchioMpi3DWrite(CbenchioWrite):
    """Measure the bandwidth of the filesystem for a single file written by all processes in a 3D layout."""

    operation = "write"
    config = "mpi-3D.yaml"
    file_per_process = False
    dimensions = 3
    fields = 4
    n_dimensions = 3
    stripe_size = 4194304
    nodes = parameter([1, 4, 8])
    tasks_per_node = parameter([288])
    base_path = parameter(["/work/z19/shared/io_benchmarks"])
    api = "mpi"
    stripes = parameter([-1])
    field_size_per_process_per_dimension = parameter([1024])


CbenchioMpi3DRead = make_read_test(CbenchioMpi3DWrite)
