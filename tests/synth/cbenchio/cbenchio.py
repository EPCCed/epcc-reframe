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

Base and meta classes for cbenchio benchmarks

"""

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



class cbenchio(rfm.RunOnlyRegressionTest):

    tags = {"performance", "io"}
    
    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    maintainers = ["l.parisi@epcc.ed.ac.uk"]
    config = None
    modules = ["cbenchio-gcc"]

    def __init__(self):
        super().__init__()
    
    executable = "benchio"
    executable_opts = ["config.yaml"]

    def write_config(self, config):
        """ Write the configuration for cbenchio to a yaml file. """
        
        filename = os.path.join(self.stagedir, "config.yaml")
        
        with open(filename, 'w') as file:
            yaml.dump( {
            "benchmarks" : [config]
        }, file, Dumper=yaml.Dumper)
    
    @sanity_function
    def completed(self):
        return sn.assert_found(r'Done', self.stdout) and sn.assert_true(os.path.exists( "report.yaml"))

    @run_before('performance')
    def extract_bandwidth(self):
            
        report_file = os.path.join(self.stagedir, "report.yaml")
        with open(report_file, 'r') as file:
            report = yaml.load(file, Loader=yaml.Loader)

        bandwidths = [ result["bandwidth"] for result in report["benchmarks"][0]["results"] ] # Bandwidths measurements for each repeat of the benchmark.
        self.perf_variables = {}
        for i in range(len(bandwidths)):
            self.perf_variables[f"bandwidth_{i}"] = sn.make_performance_function(lambda i=i: float(bandwidths[i]), "GB/s")
        

    
class cbenchio_write(cbenchio):

    
    def set_default_parameter(self, param_name, default_value):
        """ Set a default value for a parameter if it is not already set. 
        
        Might be done using custom setters and getters, but reframe's metaprogramming might interfere with that.
        """
        if not hasattr(self, param_name):
            setattr(self, param_name, default_value)
        # 

    def set_default_parameters(self):
        """ Set default values for parameters if they are not already set. This is needed as parameters are define at instance creation and will raise an error if the field is not defined, instead of overwriting. That means initialisation need to happen after the instance is initialised. """
        
        self.set_default_parameter("field_size_per_process_per_dimension", 1048576)
        self.set_default_parameter("repeat", 8)
        self.set_default_parameter("stripe_size", 1048576)
        self.set_default_parameter("stripes", 1)
        self.set_default_parameter("random_strided", False)
        self.set_default_parameter("file_per_process", True)
        self.set_default_parameter("fields", 1)
        self.set_default_parameter("n_dimensions", 1)
        self.set_default_parameter("decomposition", "slab")

    def create_write_directories(self):
            """ If writing data, create the target directory. """
            
            self.prerun_cmds=[]
            
            self.prerun_cmds.append(f"rm -rf {self.path}") # Cleaun up any previously written data
            self.prerun_cmds.append(f"mkdir -p {self.path}") # Create the directory where to write the data

            if self.stripes=="num_nodes":
                self.stripes=self.nodes

            if self.stripes != 1: # Only valid on Lustre filesystem
                self.prerun_cmds.append(f"lfs setstripe -C {self.stripes} -S {int(self.stripe_size/2**10)}K {self.path}")
            self.prerun_cmds.append(f"chmod -R o+wXr {self.path}") # Allow anyone to delete the data from the benchmarks if not properly cleaned up





    @run_before('run')
    def init_parameters(self):
        self.num_tasks = self.nodes * self.tasks_per_node
        self.num_tasks_per_node = self.tasks_per_node
        self.num_cpus_per_task = self.current_partition.processor.num_cpus // self.num_tasks_per_node
        self.path= os.path.join(self.base_path, f"{self.short_name}")
        self.set_default_parameters() # Set default values for parameters if they are not already set.
        self.cbenchio_config=self.generate_config() # Generate the parameters for cbenchio executable
        self.write_config(self.cbenchio_config)
        self.create_write_directories()


    def generate_config(self):
        """ Generates the yaml file as input to cbenchio"""

        config={
            "name": "bandwidth_test",
            "API": self.api,
            "processorGrid": [0,0,0],
            "repeat": self.repeat,
            "sync": True,
            "operation": "write",
            "content": "random",
            "alignment": 4096,
            "fields": self.fields
        }
        


        config["filePerProcess"]=self.file_per_process
        config["paths"]=[ self.path ]
        type_size = 8 # (Bytes) Assuming we are writing 64-bit floating point numbers.

        if config["API"] == "posix": # Chunk size and pattern is only supported for Posix
            config["chunkSize"] = int(self.chunk_size / type_size) # Convert from bytes to number of elements (assuming 64-bit floating point numbers)
            config["randomStrided"] = self.random_strided
        
        
        n_elements_per_process_per_dim = int(self.field_size_per_process_per_dimension /( type_size) ) # Total number of elements to write per process.

        # Compute domain decomposition and shape
        config["shape"] = [1,1,1]
        
        if self.api == "posix":
            assert self.n_dimensions == 1, "Posix API only supports 1 dimension"
        
        assert self.n_dimensions <= 3, "Only up to 3 dimensions are supported"

        assert self.decomposition == "slab", "Only slab decomposition is supported for now"
        for d in range(3):
            
            if d < self.n_dimensions:
                config["shape"][d] = n_elements_per_process_per_dim
        
        if not self.file_per_process:
            config["processorGrid"] = [self.num_tasks,0,0]
            config["shape"][0] = n_elements_per_process_per_dim * self.num_tasks
        
        return config

class cbenchio_read(cbenchio):

    @run_before("run")
    def set_read_parameters(self):
        cbenchio_config=self.write_test.cbenchio_config

        # Create mirror read operation
        cbenchio_config["operation"] = "read"
        cbenchio_config["sync"]=False
        cbenchio_config["checkReads"]=False
        self.write_config(cbenchio_config)

        # Submission parameters for the read test are the same as the write test
        self.num_tasks = self.write_test.num_tasks
        self.num_tasks_per_node = self.write_test.num_tasks_per_node
        self.num_cpus_per_task = self.write_test.num_cpus_per_task
        self.path = self.write_test.path

    @run_before("cleanup")
    def cleanup_written_files(self):
        """  Cleanup the I/O directory after read tests, as we assume that the data is not needed afterwards.
        We do not remove the data for write tests, as the data might be needed from other tests for reading.
        """
        # Remove the directory in path once we are done reading them. 

        try:
            os.system(f"rm -rf {self.path}")
        except Exception as e:
            print(f"Warning: Failed to clean up directory {self.path}: {e}")

    
def make_read_test(cls):

    # check that the class contains write
    if cls.__name__.find("write") == -1:
        raise ValueError("The class passed to make_read_test must contain 'write' in its name")

    fixture = rfm.core.builtins.fixture(cls, scope='environment')
    module=fixture.cls.__module__
    return rfm.simple_test(rfm.core.meta.make_test(cls.__name__.replace("write", "read"), (cbenchio_read,), {"operation": "read","write_test": fixture,}, module=module) )
