# EPCC ReFrame

Repository for ReFrame configuration and tests for EPCC systems.

## Structure

  - `configuration/`: configuration files for different EPCC systems
  - `tests/`: test library. All tests should, wherever possible, be configured so that they can run on all systems

## Modifications to ReFrame source


## ARCHER2 test execution

### Run all tests

To run the full suite of tests on ARCHER2, run the following commands:

```
module load reframe
module load epcc-reframe

epcc-reframe -r
```

The last command is just a wrapper around ReFrame to call all the tests and use the ARCHER2 configuration. The `-r` is the run flag in ReFrame.

### Run specific tests

Alternatively you may only wish to run a subset of tests.

Again load the modules to enable ReFrame.

```
module load reframe
module load epcc-reframe
```

To run a specific test

```
reframe -C ${EPCC_REFRAME_CONFIG} -c *path-to-a-test* -r
```

To run all tests in a directory:

```
reframe -C ${EPCC_REFRAME_CONFIG} -c *path-to-a-test-directory* -R -r
```

Where `EPCC_REFRAME_CONFIG` is set by the `epcc-reframe` module and is the path for the ARCHER2 configuration.

### Cirrus support


Compile ReFrame 4.2.0:

```bash
export PRFX=/path/to/work/
cd $PRFX

git clone https://github.com/reframe-hpc/reframe.git
cd reframe
./bootstrap.sh
./bin/reframe -V
# 4.3.0-dev.0+5e5e94c3

# Example Hello-World test:
./bin/reframe -c tutorials/basics/hello/hello1.py -r
```

Clone the Cirrus development branch of EPCC-REFRAME:
```bash
cd $PRFX

git clone https://github.com/eleanor-broadway/epcc-reframe.git --branch cirrus-dev
cd $PRFX/epcc-reframe

export PATH=$PATH:$PRFX/reframe/bin/
export EPCC_REFRAME_CONFIG=$PRFX/epcc-reframe/configuration/cirrus_settings_dev.py
export EPCC_REFRAME_TEST_DIR=$PRFX/epcc-reframe/tests

# Run an individual test:
reframe -C ${EPCC_REFRAME_CONFIG} -c tests/compile -r -R
# Run the entire test suite:
bin/epcc-reframe -r

# NOTE: currently, the entire test suite only runs the compile and libs tests.
```


<!-- The following launchers should be added to the `reframe/core/launchers/mpi.py` to define launchers for Intel MPI and HPE MPT. Added after the definition for the `mpiexec` launcher.

```python
@register_launcher('impi')
class MpiexecLauncher(JobLauncher):
    def command(self, job):
        return ['mpirun', '-ppn', str(job.num_tasks_per_node), '-n', str(job.num_tasks)]

@register_launcher('hpempt')
class MpiexecLauncher(JobLauncher):
    def command(self, job):
        return ['mpiexec_mpt', '-ppn', str(job.num_tasks_per_node), '-n', str(job.num_tasks)]
# HPE MPT mpiexec_mpt has to be used within a job (will not work with 'local' scheduler)
``` -->
