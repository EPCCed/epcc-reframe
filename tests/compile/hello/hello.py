import reframe.utility.sanity as sn
import reframe as rfm

@rfm.simple_test
class HelloTest(rfm.RegressionTest):
    
    lang=parameter(['c','cpp','f90'])
    
    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.sourcepath = f'hello.{self.lang}'
        self.sanity_patterns = sn.assert_found(r'Hello, World\!', self.stdout)
        self.extra_resources = {
                'qos': {'qos': 'standard'}
        }
        self.tags = {'functionality','short'}

