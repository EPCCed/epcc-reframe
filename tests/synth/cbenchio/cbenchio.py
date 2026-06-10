#!/usr/bin/env python3
"""
CBenchio Input/Output test

"""

from fileinput import filename
import os
from tempfile import template

import yaml

import reframe as rfm
import reframe.utility.sanity as sn
import numpy as np

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from reframe.core.builtins import (
    fixture
)

class cbenchio(rfm.RunOnlyRegressionTest):
    tags = {"performance", "io"}

    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    maintainers = ["l.parisi@epcc.ed.ac.uk"]



    def __init__(self):
        super().__init__()
    executable = "/work/z19/z19/lparisi/nfs-testing/cbenchio/opt/cbenchio/dev/bin/benchio"  
    executable_opts = ["config.yaml"]


class cbenchio_bandwidthBase(cbenchio):

    num_tasks_per_core = 1
    chunk_size = 4096 # KiB
    file_size_per_process = 1024 # MiB
    repeat= 20
    tasks = parameter([1 ])
    base_path=parameter(["/work/z19/z19/lparisi/nfs-testing/runs/data"])

    @run_after('init')
    def init_parameters(self):
        self.num_tasks = self.tasks
        self.path= os.path.join(self.base_path, f"bandwidth_{self.tasks}_tasks")

    @run_after('setup')
    def generate_config(self):
        
        config={
            "name": "bandwidth_test",
            "API": "posix",
            "filePerProcess": True,
            "processorGrid": [0,0,0],
            "repeat": self.repeat,
            "sync": True,
            "operation": self.operation,
            "content": "random",
            "alignment": 4096,
            "fields": 1
        }

        config["paths"]=[ self.path ]
        type_size = 8 # (Bytes) Assuming we are writing 64-bit floating point numbers.
        config["chunkSize"] = int(self.chunk_size * 2**10 / type_size) # Convert from KiB to number of elements (assuming 64-bit floating point numbers)
        n_elements = int(self.file_size_per_process * 2**20 /( type_size)) # Total number of elements to write per process.
        config["shape"] = [n_elements, 1, 1] # Sets the shape of the data to write.
        config["randomStrided"] = False

        
        # Write the configuration to a yaml file
        filename = os.path.join(self.stagedir, "config.yaml")
        with open(filename, 'w') as file:
            yaml.dump( {
            "benchmarks" : [config]
        }, file, Dumper=yaml.Dumper)
    
    @run_before('run')
    def create_directories(self):
            os.makedirs(self.path, exist_ok=True)
    
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



    
class cbenchio_bandwidth_write(cbenchio_bandwidthBase):
    operation = "write"

@rfm.simple_test
class cbenchio_bandwidth_read(cbenchio_bandwidthBase):
    operation = "read"
    bandwidth_write_text = fixture(cbenchio_bandwidth_write, scope='environment')

    @run_before("cleanup")
    def cleanup_written_files(self):
        # Remote the directory in path 
        if os.path.exists(self.path):
            os.system(f"rm -rf {self.path}")