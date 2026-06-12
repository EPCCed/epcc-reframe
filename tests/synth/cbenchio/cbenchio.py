#!/usr/bin/env python3
"""
CBenchio Input/Output test
"""

from fileinput import filename
import os
from tempfile import template
import types
from typing import List
import yaml

import reframe as rfm
import reframe.utility.sanity as sn
import numpy as np
import reframe.core.builtins as builtins

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from reframe.core.builtins import (
    fixture
)
import reframe.core.meta as meta


""" Cbenchio tests

Used for I/O benchmarking.

## Adding new tests

Add a new test by inherting from cbenchio_bandwidthBase and using the Parameterize metaclass. The class should have a config attribute pointing to a yaml file. The yaml file should contain the parameters for the test. For example:

```python
class cbenchio_bandwidth_write(cbenchio_bandwidthBase,metaclass=Parameterize):
    operation = "write"
    config= "posix.yaml"
```

Read tests can be generated from write tests using the make_read_test function. For example we can generate a read test from the write test above using:

```python
cbenchio_bandwidth_read = make_read_test(cbenchio_bandwidth_write)
```

"""

class cbenchio(rfm.RunOnlyRegressionTest):
    tags = {"performance", "io"}

    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    maintainers = ["l.parisi@epcc.ed.ac.uk"]



    def __init__(self):
        super().__init__()
    executable = "/work/z19/z19/lparisi/nfs-testing/cbenchio/opt/cbenchio/dev/bin/benchio"  
    executable_opts = ["config.yaml"]


def expand_combinations(parameters: dict) -> List[dict]:
    """
    
    Args:
        parameters: A dictionary where each key is a parameter name and each value is a list of values for that parameter.
        repeats: The number of times to repeat each combination of parameters.
    """
    
    combinations = []
    
    for key, values in parameters.items():
        new_combinations = []
        for value in values:
            for combination in combinations:
                new_combination = combination.copy()
                new_combination.update({key: value})
                new_combinations.append(new_combination)
        combinations = new_combinations.copy()
    
    return combinations


def get_config(filename: str) -> dict:
    """ Read parameters from a yaml file

    Args:
        filename: The name of the yaml file containing the parameters. The file should be located in the same directory as this script.
    Returns:        A dictionary containing the parameters read from the yaml file.
    
    """

    filename=os.path.join(os.path.dirname(__file__), filename) # Filename is relative to the location of this script


    with open(filename, "r") as f:
        config = yaml.load(f, Loader=Loader)
    return config

class Parameterize(meta.RegressionTestMeta):
    """ Metaclass to parameterize a regression test based on a yaml configuration file.
    The yaml file should contain a dictionary where each key is a parameter name and each value is a list of values for that parameter. The metaclass will turn these into parameters. This cannot be done in __init__() because the subsitution need to be done before the instance is created. 
    """


    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        mapping =  super().__prepare__( name, bases)
        return mapping
    
    def __new__(cls, name, bases, namespace,*args, **kwds):
        
        # Turn all labels in the yaml configuration
        config = get_config(namespace["config"])
        for parameter_name,parameter_values in config.items():
            namespace[parameter_name] = builtins.parameter(parameter_values)

        obj = super().__new__(cls,name,bases,namespace,*args, **kwds)
        return obj

class cbenchio_bandwidthBase(cbenchio):

    
    num_tasks_per_core = 1
    file_size_per_process = 1024 # MiB
    repeat= 5
    stripe_size = 4096 # KiB
    stripes = None # Number of stripes to use. Only valid if writing to a Lustre filesystem
    random_strided = False # Whether to use random strided access pattern. Only valid for read tests.
    file_per_process = True

    @run_before('run')
    def init_parameters(self):
        self.num_tasks = self.nodes * self.tasks_per_node
        self.num_tasks_per_node = self.tasks_per_node
        self.num_cpus_per_task = self.current_partition.processor.num_cpus // self.num_tasks_per_node
        self.path= os.path.join(self.base_path, f"bandwidth_nodes_{self.nodes}_tasks_per_node_{self.tasks_per_node}")
        self.generate_config()
        self.create_directories()


    def generate_config(self):
        """ Generates the yaml file as input to cbenchio"""

        config={
            "name": "bandwidth_test",
            "API": self.api,
            "processorGrid": [0,0,0],
            "repeat": self.repeat,
            "sync": True,
            "operation": self.operation,
            "content": "random",
            "alignment": 4096,
            "fields": 1
        }

        if self.operation == "read":
            config["sync"] = False
        config["filePerProcess"]=self.file_per_process
        config["paths"]=[ self.path ]
        type_size = 8 # (Bytes) Assuming we are writing 64-bit floating point numbers.
        config["chunkSize"] = int(self.chunk_size * 2**10 / type_size) # Convert from KiB to number of elements (assuming 64-bit floating point numbers)
        if self.file_per_process:
            n_elements = int(self.file_size_per_process * 2**20 /( type_size)) # Total number of elements to write per process.
        else:
            n_elements = int(self.file_size_per_process * self.num_tasks * 2**20 / (type_size)) # Total number of elements to write if all processes write to the same file.


        config["shape"] = [n_elements, 1, 1] # Use a 1D array
        config["randomStrided"] = self.random_strided
        
        # Write the configuration to a yaml file
        filename = os.path.join(self.stagedir, "config.yaml")
        with open(filename, 'w') as file:
            yaml.dump( {
            "benchmarks" : [config]
        }, file, Dumper=yaml.Dumper)
            
        
    
    def create_directories(self):
            """ If writing data, create the target directory. """
            
            self.prerun_cmds=[]
            if self.operation == "write":
                self.prerun_cmds.append(f"rm -rf {self.path}") # Cleaun up any previously written data
                self.prerun_cmds.append(f"mkdir -p {self.path}") # Create the directory where to write the data
                self.prerun_cmds.append(f"chmod -R o+wXr {self.path}") # Allow anyone to delete the data from the benchmarks if not properly cleaned up

                if self.stripes is not None: # Only valid on Lustre filesystem
                    self.prerun_cmds.append(f"lfs setstripe -C {self.stripes} -S {self.stripe_size} {self.path}")
                
    
    @sanity_function
    def completed(self):
        return sn.assert_found(r'Done', self.stdout) and sn.assert_true(os.path.exists( "report.yaml"))

    @run_before('performance')
    def extract_bandwidth(self):

        # Read the report.yaml file and extract the bandwidth value
        report_file = os.path.join(self.stagedir, "report.yaml")
        with open(report_file, 'r') as file:
            report = yaml.load(file, Loader=yaml.Loader)

        bandwidth = [ result["bandwidth"] for result in report["benchmarks"][0]["results"] ]

        self.perf_variables = {
            "bandwidth_mean": sn.make_performance_function(lambda : np.mean(bandwidth), "GB/s"),
            "bandwidth_max": sn.make_performance_function(lambda : np.max(bandwidth), "GB/s"),
            "bandwidth_min": sn.make_performance_function(lambda : np.min(bandwidth), "GB/s"),
            "bandwidth_std": sn.make_performance_function(lambda : np.std(bandwidth), "GB/s"),
            
        }
    

    @run_before("cleanup")
    def cleanup_written_files(self):
        """  Cleanup the I/O directory after read tests, as we assume that the data is not needed afterwards.
        We do not remove the data for write tests, as the data might be needed from other tests for reading.
        """
        # Remove the directory in path once we are done reading them. 
        if os.path.exists(self.path) and self.operation == "read":
            try:
                os.system(f"rm -rf {self.path}")
            except Exception as e:
                print(f"Warning: Failed to clean up directory {self.path}: {e}")


def make_read_test(cls):
    
    def set_read_parameters(self):
        """Set parameters for read test based on the write test"""

        config = get_config(self.write_test.config)
        for parameter_name in config.keys():
            setattr(self, parameter_name, getattr(self.write_test, parameter_name))

    rfm.simple_test(rfm.core.meta.make_test(cls.__name__.replace("write", "read"), (cbenchio_bandwidthBase,), {"operation": "read","write_test": fixture(cls, scope='environment'),}, methods=[rfm.core.builtins.run_after("setup")(set_read_parameters)], module=__name__))


class cbenchio_posix_sequential_write(cbenchio_bandwidthBase,metaclass=Parameterize):
    """ Measure the bandwidth of the filesystem for file per process patterns for large sequential I/O. """
    operation = "write"
    config= "posix-large-sequential.yaml"

cbenchio_posix_sequential_read = make_read_test(cbenchio_posix_sequential_write)


class cbenchio_posix_random_write(cbenchio_bandwidthBase,metaclass=Parameterize):
    """ Measure the bandwidth of the filesystem for file per process patterns random 4KiB I/O. """
    operation = "write"
    config= "posix-large-random.yaml"

cbenchio_posix_random_read = make_read_test(cbenchio_posix_random_write)
