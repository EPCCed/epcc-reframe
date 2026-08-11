"""Cbenchio benchmarks

Contains I/O benchmarks based on cbenchio.

"""

from cbenchio import CbenchioWrite, make_read_test

# Needs to import reframe so that the test runner can find the test classes,
# even if they are not used directly in this file.
# pylint: disable=unused-import
# flake8: noqa: F401
import reframe as rfm

# pylint: enable=unused-import
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
