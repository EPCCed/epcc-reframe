#!/usr/bin/env python3
"""
Containerised OSU benchmarks

These tests checks that containers can be run with MPI. Basic performance checks are also included.
"""

import os

import reframe as rfm
import reframe.utility.sanity as sn


class PullOSUContainerARCHER2(rfm.RunOnlyRegressionTest):
    """Pull a container containing an osu benchmark - GLIBC compatible with ARCHER2 OS"""

    descr = "Pull an OSU benchmark container from github "
    valid_systems = ["archer2:login"]
    valid_prog_environs = ["PrgEnv-gnu"]
    executable = "singularity"
    image_name = "archer2_osu"
    executable_opts = ["pull", f"docker://ghcr.io/epcced/epcc-reframe/{image_name}"]
    local = True

    @sanity_function
    def validate_download(self):
        """Sanity Check"""
        return sn.assert_not_found("error", self.stderr)


class PullOSUContainerCirrusEX(rfm.RunOnlyRegressionTest):
    """Pull a container containing an osu benchmark - GLIBC compatible with CirrusEX OS"""

    descr = "Pull an OSU benchmark container from github "
    valid_systems = ["cirrus-ex:login"]
    valid_prog_environs = ["PrgEnv-gnu"]
    executable = "apptainer"
    image_name = "osu-benchmarks"
    image_version = "7.5.1"
    executable_opts = ["pull", f"docker://ghcr.io/epcced/epcc-reframe/{image_name}:{image_version}"]
    local = True

    @sanity_function
    def validate_download(self):
        """Sanity Check"""
        return sn.assert_not_found("error", self.stderr)


@rfm.simple_test
class OSUContainerTestARCHER2(rfm.RunOnlyRegressionTest):
    """Run the OSU benchmark in a container"""

    descr = "OSU benchmarks in a container"
    osu_container = fixture(PullOSUContainerARCHER2, scope="session")
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    num_tasks = 256
    num_tasks_per_node = 128
    num_cpus_per_task = 1
    time_limit = "5m"

    env_vars = {
        "OMP_NUM_THREADS": str(num_cpus_per_task),
        "OMP_PLACES": "cores",
        "SINGULARITYENV_LD_LIBRARY_PATH": "/opt/cray/pe/mpich/8.1.23/ofi/gnu/9.1/lib-abi-mpich:\
/opt/cray/pe/mpich/8.1.23/gtl/lib:/opt/cray/libfabric/1.12.1.2.2.0.0/lib64:\
/opt/cray/pe/gcc-libs:/opt/cray/pe/gcc-libs:/opt/cray/pe/lib64:/opt/cray/pe/lib64:\
/opt/cray/xpmem/default/lib64:/usr/lib64/libibverbs:/usr/lib64:/usr/lib64",
        "SINGULARITY_BIND": "/opt/cray,/var/spool,\
/opt/cray/pe/mpich/8.1.23/ofi/gnu/9.1/lib-abi-mpich:\
/opt/cray/pe/mpich/8.1.23/gtl/lib,/etc/host.conf,\
/etc/libibverbs.d/mlx5.driver,/etc/libnl/classid,\
/etc/resolv.conf,/opt/cray/libfabric/1.12.1.2.2.0.0/lib64/libfabric.so.1,\
/opt/cray/pe/gcc-libs/libatomic.so.1,/opt/cray/pe/gcc-libs/libgcc_s.so.1,\
/opt/cray/pe/gcc-libs/libgfortran.so.5,/opt/cray/pe/gcc-libs/libquadmath.so.0,\
/opt/cray/pe/lib64/libpals.so.0,/opt/cray/pe/lib64/libpmi2.so.0,\
/opt/cray/pe/lib64/libpmi.so.0,/opt/cray/xpmem/default/lib64/libxpmem.so.0,\
/run/munge/munge.socket.2,/usr/lib64/libibverbs/libmlx5-rdmav34.so,\
/usr/lib64/libibverbs.so.1,/usr/lib64/libkeyutils.so.1,/usr/lib64/liblnetconfig.so.4,\
/usr/lib64/liblustreapi.so,/usr/lib64/libmunge.so.2,/usr/lib64/libnl-3.so.200,\
/usr/lib64/libnl-genl-3.so.200,/usr/lib64/libnl-route-3.so.200,/usr/lib64/librdmacm.so.1,\
/usr/lib64/libyaml-0.so.2",
    }

    reference = {
        "archer2:compute": {"latency_big": (2200, -0.02, 0.30, "us"), "latency_small": (8.4, -0.05, 0.30, "us")}
    }

    @require_deps
    def set_singularity_invoke(self):
        """Builds the command to be passed to srun"""
        self.executable = "singularity"

        self.executable_opts = [
            "run",
            os.path.join(self.osu_container.stagedir, self.osu_container.image_name + "_latest.sif"),
            "osu_allreduce",
        ]

    @performance_function("us")
    def latency_big(self):
        """Extract the latency from the largest size in the OSU test"""
        return sn.extractsingle(r"^1048576\W+([0-9]+(?:.[0-9]+)?)", self.stdout, 1, float)

    @performance_function("us")
    def latency_small(self):
        """Extract the latency from the largest size in the OSU test"""
        return sn.extractsingle(r"^4\W+([0-9]+(?:.[0-9]+)?)", self.stdout, 1, float)

    @sanity_function
    def validate_job_run(self):
        """Basic check that any output was produced"""
        return sn.assert_found("OSU MPI Allreduce Latency Test ", self.stdout)


@rfm.simple_test
class OSUContainerTestCirrusEX(rfm.RunOnlyRegressionTest):
    """Run the OSU benchmark in a container"""

    descr = "OSU benchmarks in a container"
    osu_container = fixture(PullOSUContainerCirrusEX, scope="session")
    valid_systems = ["cirrus-ex:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]
    num_tasks = 576
    num_tasks_per_node = 288
    num_cpus_per_task = 1
    time_limit = "10m"

    env_vars = {
        "OMP_NUM_THREADS": str(num_cpus_per_task),
        "OMP_PLACES": "cores",
        "APPTAINERENV_LD_LIBRARY_PATH": "/opt/cray/pe/mpich/8.1.32/ofi/gnu/11.2/lib-abi-mpich:\
/opt/cray/libfabric/2.3.1/lib64:\
/opt/cray/pals/1.6/lib:\
/opt/cray/pe/lib64:\
/opt/xpmem/lib64:/lib64",
        "APPTAINER_BIND": "/opt/cray,/var/spool,\
/opt/cray/pe/mpich/8.1.32/ofi/gnu/11.2/lib-abi-mpich,\
/etc/host.conf,/etc/libibverbs.d/mlx5.driver,\
/etc/libnl/classid,\
/etc/resolv.conf,\
/opt/cray/libfabric/2.3.1/lib64/libfabric.so.1,\
/lib64/libatomic.so.1,\
/lib64/libgcc_s.so.1,/lib64/libgfortran.so.5,\
/lib64/libquadmath.so.0,\
/opt/cray/pals/1.6/lib/libpals.so.0,\
/opt/cray/pe/lib64/libpmi2.so.0,\
/opt/cray/pe/lib64/libpmi.so.0,\
/opt/xpmem/lib64/libxpmem.so.0,\
/run/munge/munge.socket.2,\
/lib64/libmunge.so.2,\
/lib64/libnl-3.so.200,\
/lib64/libnl-genl-3.so.200,\
/lib64/libnl-route-3.so.200,\
/lib64/librdmacm.so.1,\
/lib64/libcxi.so.1,\
/lib64/libm.so.6",
    }

    reference = {
        "cirrus-ex:compute": {"latency_big": (1100, -0.1, 0.30, "us"), "latency_small": (9.7, -0.1, 0.30, "us")}
    }
    
    @require_deps
    def set_singularity_invoke(self):
        """Builds the command to be passed to srun"""
        self.executable = "apptainer"

        self.executable_opts = [
            "run",
            os.path.join(
                self.osu_container.stagedir,
                self.osu_container.image_name + "_" + self.osu_container.image_version + ".sif",
            ),
            "osu_allreduce",
        ]

    @performance_function("us")
    def latency_big(self):
        """Extract the latency from the largest size in the OSU test"""
        return sn.extractsingle(r"^1048576\W+([0-9]+(?:.[0-9]+)?)", self.stdout, 1, float)

    @performance_function("us")
    def latency_small(self):
        """Extract the latency from the largest size in the OSU test"""
        return sn.extractsingle(r"^4\W+([0-9]+(?:.[0-9]+)?)", self.stdout, 1, float)

    @sanity_function
    def validate_job_run(self):
        """Basic check that any output was produced"""
        return sn.assert_found("OSU MPI Allreduce Latency Test ", self.stdout)
