#!/usr/bin/env python3

"""Resnet50 base class"""

import reframe as rfm
import reframe.utility.sanity as sn


class ResNet50BaseCheck(rfm.RunOnlyRegressionTest):
    """Resnet50 base class"""

    @performance_function("", perf_key="Delta Loss")
    def extract_delta_loss(self):
        """Extracts data loss"""
        return sn.extractsingle(
            r"Change In Train Loss at Epoch: (.*)",
            self.stdout,
            tag=1,
            conv=float,
        )

    @performance_function("inputs/s", perf_key="Throughput")
    def extract_throughput(self):
        """Extracts throughput"""
        speeds = sn.extractall(r"Processing Speed: (.*)", self.stdout, tag=1, conv=float)
        return sum(map(float, speeds)) / len(list(speeds))

    @performance_function("s", perf_key="Communication Time")
    def extract_communication(self):
        """Extracts communication time"""
        times = sn.extractall(r"Communication Time: (.*)", self.stdout, tag=1, conv=float)
        return sum(map(float, times)) / len(list(times))

    @performance_function("s", perf_key="Epoch Length")
    def extract_epoch_length(self):
        """Extracts epoch length"""
        times = sn.extractall(r"Time For Epoch: (.*)", self.stdout, tag=1, conv=float)
        return sum(map(float, times)) / len(list(times))

    @performance_function("s", perf_key="Total IO Time")
    def extract_io(self):
        """Extracts total io time"""
        times = sn.extractall(r"Total IO Time: (.*)", self.stdout, tag=1, conv=float)
        return sum(map(float, times)) / len(list(times))

    @sanity_function
    def assert_target_met(self):
        """Asserts test ran successfully"""
        return sn.assert_found(r"Processing Speed", filename=self.stdout)

    @run_before("performance")
    def set_perf_variables(self):
        """Sets up performance variables"""
        self.perf_variables = {
            "Throughput": self.extract_throughput(),
            "Epoch Length": self.extract_epoch_length(),
            "Delta Loss": self.extract_delta_loss(),
            "Communication Time": self.extract_communication(),
            "Total IO Time": self.extract_io(),
        }
