from cbenchio import cbenchio_write,Parameterize,cbenchio_read,make_read_test

import reframe as rfm

""" Cbenchio benchmarks

Contains I/O benchmarks based on cbenchio.

## Adding new tests

Add a new test by inherting from cbenchio_write and using the Parameterize metaclass. The class should have a config attribute pointing to a yaml file. The yaml file should contain the parameters for the test. For example:

```python
class cbenchio_bandwidth_write(cbenchio_write,metaclass=Parameterize):
    operation = "write"
    config= "posix.yaml"
```

Read tests can be generated from write tests using the make_read_test function. For example we can generate a read test from the write test above using:

```python
cbenchio_bandwidth_read = make_read_test(cbenchio_bandwidth_write)
```

"""


class cbenchio_posix_sequential_write(cbenchio_write,metaclass=Parameterize):
    """ Measure the bandwidth of the filesystem for file per process patterns for large sequential I/O. """
    operation = "write"
    config= "posix-large-sequential.yaml"

cbenchio_posix_sequential_read = make_read_test(cbenchio_posix_sequential_write)

class cbenchio_posix_random_write(cbenchio_write,metaclass=Parameterize):
    """ Measure the bandwidth of the filesystem for file per process patterns random 4KiB I/O. """
    operation = "write"
    config= "posix-large-random.yaml"
    random_strided = True
    max_random_stride = 4096 # KiB
    file_size_per_process = 4 # MiB

cbenchio_posix_random_read = make_read_test(cbenchio_posix_random_write)