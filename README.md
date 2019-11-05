# EPCC Reframe

Repository for Reframe configuration and tests for EPCC systems

## Structure

  - `configuration/`: configuration files for different EPCC systems
  - `tests/`: test library. All tests should, wherever possible, be configured so that they can run on all systems
  
## Modifications to reframe source

### Cirrus support

The following launchers should be added to the `reframe/core/launchers/mpi.py` to define launchers for Intel MPI and HPE MPT. Added after the definition for the `mpiexec` launcher.

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
```
