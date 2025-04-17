"""ReFrame Base Quantum Espresso (QE)"""

import reframe as rfm
import reframe.utility.sanity as sn


class QEBaseEnvironment(rfm.RunOnlyRegressionTest):
    """Definition of functions used for all QE ReFrame tests"""

    # Set the version of QE, i.e. 6.8, 7.1, 7.3.1
    # Warning: reduce number of tasks (i.e. 32) to use 6.8 with AUSURF
    qe_version = "7.1"
    maintainers = ["e.broadway@epcc.ed.ac.uk"]
    strict_check = True
    use_multithreading = False
    valid_systems = ["archer2:compute"]
    valid_prog_environs = ["PrgEnv-gnu"]

    @sanity_function
    def assert_finished(self):
        """Sanity check that simulation finished successfully"""
        return sn.assert_found("JOB DONE.", self.stdout)

    @run_before("performance")
    def set_perf_variables(self):
        """Build a dictionary of performance variables"""

        # Expand the variables to collect different stats, commented out below
        timings = ["PWSCF"]
        # timings = [
        #     'PWSCF', 'electrons', 'c_bands', 'cegterg', 'calbec',
        #     'fft', 'ffts', 'fftw'
        # ]

        for name in timings:
            for kind in ["cpu", "wall"]:
                res = self.extract_report_time(name, kind)
                self.perf_variables[f"{name}_{kind}"] = res

    @staticmethod
    @sn.deferrable
    def convert_timings(timing: str) -> float:
        """Convert timings to seconds"""

        if timing is None:
            return 0

        days, timing = (["0", "0"] + timing.split("d"))[-2:]
        hours, timing = (["0", "0"] + timing.split("h"))[-2:]
        minutes, timing = (["0", "0"] + timing.split("m"))[-2:]
        seconds = timing.split("s")[0]

        return float(days) * 86400 + float(hours) * 3600 + float(minutes) * 60 + float(seconds)

    @performance_function("s")
    def extract_report_time(self, name: str = None, kind: str = None) -> float:
        """Extract timings from pw.x stdout
        Args:
            name (str, optional): Name of the timing to extract.
            kind (str, optional): Kind ('cpu' or 'wall) of timing to extract.
        Raises:
            ValueError: If the kind is not 'cpu' or 'wall'
        Returns:
            float: The timing in seconds
        """

        if kind is None:
            return 0
        kind = kind.lower()
        if kind == "cpu":
            tag = 1
        elif kind == "wall":
            tag = 2
        else:
            raise ValueError(f"unknown kind: {kind}")

        # Possible formats
        #       PWSCF        :   4d 6h19m CPU  10d14h38m WALL

        execute_time = self.convert_timings(
            sn.extractsingle(rf"{name}\s+:\s+(.+)\s+CPU\s+(.+)\s+WALL", self.stdout, tag, str).evaluate()
        )
        return execute_time
